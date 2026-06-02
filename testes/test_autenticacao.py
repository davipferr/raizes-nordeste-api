from testes.conftest import cabecalho

def test_t01_login_valido(cliente_http):
    resposta = cliente_http.post("/auth/login", json={"email": "admin@teste.com", "senha": "Teste@123"})
    assert resposta.status_code == 200
    dados = resposta.json()
    assert "access_token" in dados
    assert dados["token_type"] == "Bearer"
    assert dados["usuario"]["perfil"] == "ADMIN"

def test_t02_cadastro_novo_usuario(cliente_http):
    resposta = cliente_http.post("/auth/registrar", json={
        "nome": "Novo Usuário Teste",
        "email": "novousuario_unico@teste.com",
        "senha": "Senha@123",
        "perfil": "CLIENTE",
        "consentimento_lgpd": True,
    })
    assert resposta.status_code == 201
    dados = resposta.json()
    assert dados["email"] == "novousuario_unico@teste.com"
    assert "senha" not in dados
    assert "senha_hash" not in dados

def test_t07_acesso_sem_token(cliente_http):
    resposta = cliente_http.get("/pedidos")
    assert resposta.status_code == 401
    corpo = resposta.json()
    assert "erro" in corpo or "detail" in corpo

def test_t08_acesso_com_perfil_sem_permissao(cliente_http, token_cliente):
    resposta = cliente_http.post(
        "/estoque/entrada",
        json={"unidade_id": 1, "produto_id": 1, "quantidade": 10},
        headers=cabecalho(token_cliente),
    )
    assert resposta.status_code == 403
    corpo = resposta.json()
    assert corpo.get("erro") == "PERMISSAO_NEGADA"

def test_t11_login_senha_errada(cliente_http):
    resposta = cliente_http.post("/auth/login", json={"email": "admin@teste.com", "senha": "SenhaErrada"})
    assert resposta.status_code == 401
    corpo = resposta.json()
    assert corpo.get("erro") == "CREDENCIAIS_INVALIDAS"
