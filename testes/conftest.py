import os
import pytest
from datetime import datetime, timezone
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from src.api.dependencias.banco import obter_db
from src.infraestrutura.banco.modelos.modelo_base import ModeloBase
from src.infraestrutura.banco.modelos import (
    ModeloUsuario, ModeloUnidade, ModeloProduto,
    ModeloCardapioUnidade, ModeloEstoque
)
from src.infraestrutura.seguranca.servico_senha import gerar_hash
from src.dominio.enums import PerfilUsuario

_DATABASE_TEST_URL = os.environ.get(
    "DATABASE_TEST_URL",
    os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/raizes_nordeste_teste"),
)

os.environ.setdefault("DATABASE_URL", _DATABASE_TEST_URL)
os.environ.setdefault("CHAVE_SECRETA_JWT", "chave-de-teste-unitario-12345678901234")
os.environ.setdefault("ALGORITMO_JWT", "HS256")
os.environ.setdefault("MINUTOS_EXPIRACAO_TOKEN", "60")

_MOTOR_TESTE = create_engine(
    _DATABASE_TEST_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)
_SessaoTeste = sessionmaker(autocommit=False, autoflush=False, bind=_MOTOR_TESTE)

_IDS: dict = {}

def _popular_banco_teste():
    s = _SessaoTeste()
    agora = datetime.now(timezone.utc)

    admin = ModeloUsuario(nome="Admin Teste", email="admin@teste.com", senha_hash=gerar_hash("Teste@123"), perfil=PerfilUsuario.ADMIN, ativo=True, consentimento_lgpd=True, data_consentimento=agora)
    gerente = ModeloUsuario(nome="Gerente Teste", email="gerente@teste.com", senha_hash=gerar_hash("Teste@123"), perfil=PerfilUsuario.GERENTE, ativo=True, consentimento_lgpd=False)
    cozinha = ModeloUsuario(nome="Cozinha Teste", email="cozinha@teste.com", senha_hash=gerar_hash("Teste@123"), perfil=PerfilUsuario.COZINHA, ativo=True, consentimento_lgpd=False)
    atendente = ModeloUsuario(nome="Atendente Teste", email="atendente@teste.com", senha_hash=gerar_hash("Teste@123"), perfil=PerfilUsuario.ATENDENTE, ativo=True, consentimento_lgpd=False)
    cliente = ModeloUsuario(nome="Cliente Teste", email="cliente@teste.com", senha_hash=gerar_hash("Teste@123"), perfil=PerfilUsuario.CLIENTE, ativo=True, consentimento_lgpd=True, data_consentimento=agora)
    sem_lgpd = ModeloUsuario(nome="Sem LGPD", email="semconsentimento@teste.com", senha_hash=gerar_hash("Teste@123"), perfil=PerfilUsuario.CLIENTE, ativo=True, consentimento_lgpd=False)

    s.add_all([admin, gerente, cozinha, atendente, cliente, sem_lgpd])
    s.flush()

    unidade = ModeloUnidade(nome="Unidade Fortaleza Teste", endereco="Rua do Cuscuz, 1", cidade="Fortaleza", estado="CE", ativo=True)
    s.add(unidade)
    s.flush()

    p1 = ModeloProduto(nome="Cuscuz com Camarão", descricao="Desc", preco=Decimal("28.90"), categoria="Prato Principal", ativo=True)
    p2 = ModeloProduto(nome="Café Coado", descricao="Desc", preco=Decimal("6.00"), categoria="Bebidas", ativo=True)
    p3 = ModeloProduto(nome="Item Escasso", descricao="Para testar estoque insuficiente", preco=Decimal("10.00"), categoria="Outros", ativo=True)
    s.add_all([p1, p2, p3])
    s.flush()

    s.add_all([
        ModeloCardapioUnidade(unidade_id=unidade.id, produto_id=p1.id, ativo=True),
        ModeloCardapioUnidade(unidade_id=unidade.id, produto_id=p2.id, ativo=True),
        ModeloCardapioUnidade(unidade_id=unidade.id, produto_id=p3.id, ativo=True),
    ])
    s.add_all([
        ModeloEstoque(unidade_id=unidade.id, produto_id=p1.id, quantidade=500, minimo_alerta=10),
        ModeloEstoque(unidade_id=unidade.id, produto_id=p2.id, quantidade=500, minimo_alerta=10),
        ModeloEstoque(unidade_id=unidade.id, produto_id=p3.id, quantidade=1, minimo_alerta=5),
    ])
    s.commit()

    _IDS.update({
        "unidade": unidade.id,
        "produto_1": p1.id,
        "produto_2": p2.id,
        "produto_escasso": p3.id,
        "cliente_id": cliente.id,
    })
    s.close()

@pytest.fixture(scope="session", autouse=True)
def banco_inicializado():
    ModeloBase.metadata.drop_all(_MOTOR_TESTE)
    ModeloBase.metadata.create_all(_MOTOR_TESTE)
    _popular_banco_teste()
    yield
    ModeloBase.metadata.drop_all(_MOTOR_TESTE)

@pytest.fixture
def sessao():
    s = _SessaoTeste()
    yield s
    s.close()

@pytest.fixture
def cliente_http(sessao):
    def _db():
        yield sessao

    app.dependency_overrides[obter_db] = _db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def ids():
    return _IDS

@pytest.fixture
def token_admin(cliente_http):
    r = cliente_http.post("/auth/login", json={"email": "admin@teste.com", "senha": "Teste@123"})
    return r.json()["access_token"]

@pytest.fixture
def token_gerente(cliente_http):
    r = cliente_http.post("/auth/login", json={"email": "gerente@teste.com", "senha": "Teste@123"})
    return r.json()["access_token"]

@pytest.fixture
def token_cozinha(cliente_http):
    r = cliente_http.post("/auth/login", json={"email": "cozinha@teste.com", "senha": "Teste@123"})
    return r.json()["access_token"]

@pytest.fixture
def token_atendente(cliente_http):
    r = cliente_http.post("/auth/login", json={"email": "atendente@teste.com", "senha": "Teste@123"})
    return r.json()["access_token"]

@pytest.fixture
def token_cliente(cliente_http):
    r = cliente_http.post("/auth/login", json={"email": "cliente@teste.com", "senha": "Teste@123"})
    return r.json()["access_token"]

@pytest.fixture
def token_sem_lgpd(cliente_http):
    r = cliente_http.post("/auth/login", json={"email": "semconsentimento@teste.com", "senha": "Teste@123"})
    return r.json()["access_token"]

def cabecalho(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
