from datetime import datetime, timezone
from src.infraestrutura.banco.conexao import SessionMaker
from src.infraestrutura.banco.modelos import (
    ModeloUsuario, ModeloUnidade, ModeloProduto,
    ModeloCardapioUnidade, ModeloEstoque
)
from src.dominio.enums import PerfilUsuario
from passlib.context import CryptContext

contexto_crypt = CryptContext(schemes=["bcrypt"], deprecated="auto")

def popular_banco():
    sessao = SessionMaker()
    try:
        if sessao.query(ModeloUsuario).first():
            print("Banco já populado. Encerrando seed.")
            return

        admin = ModeloUsuario(
            nome="Administrador Raízes",
            email="admin@raizesnordeste.com.br",
            senha_hash=contexto_crypt.hash("Admin@123"),
            perfil=PerfilUsuario.ADMIN,
            ativo=True,
            consentimento_lgpd=True,
            data_consentimento=datetime.now(timezone.utc),
        )
        gerente = ModeloUsuario(
            nome="Maria das Dores",
            email="gerente@raizesnordeste.com.br",
            senha_hash=contexto_crypt.hash("Gerente@123"),
            perfil=PerfilUsuario.GERENTE,
            ativo=True,
            consentimento_lgpd=True,
            data_consentimento=datetime.now(timezone.utc),
        )
        cozinha = ModeloUsuario(
            nome="João Batista",
            email="cozinha@raizesnordeste.com.br",
            senha_hash=contexto_crypt.hash("Cozinha@123"),
            perfil=PerfilUsuario.COZINHA,
            ativo=True,
            consentimento_lgpd=False,
        )
        atendente = ModeloUsuario(
            nome="Ana Luiza",
            email="atendente@raizesnordeste.com.br",
            senha_hash=contexto_crypt.hash("Atendente@123"),
            perfil=PerfilUsuario.ATENDENTE,
            ativo=True,
            consentimento_lgpd=False,
        )
        cliente1 = ModeloUsuario(
            nome="Pedro Alves",
            email="cliente@raizesnordeste.com.br",
            senha_hash=contexto_crypt.hash("Cliente@123"),
            perfil=PerfilUsuario.CLIENTE,
            ativo=True,
            consentimento_lgpd=True,
            data_consentimento=datetime.now(timezone.utc),
        )
        cliente2 = ModeloUsuario(
            nome="Fernanda Lima",
            email="fernanda@email.com",
            senha_hash=contexto_crypt.hash("Cliente@123"),
            perfil=PerfilUsuario.CLIENTE,
            ativo=True,
            consentimento_lgpd=False,
        )
        sessao.add_all([admin, gerente, cozinha, atendente, cliente1, cliente2])
        sessao.flush()

        unidade_fortaleza = ModeloUnidade(
            nome="Raízes do Nordeste - Fortaleza Centro",
            endereco="Rua do Cuscuz, 42",
            cidade="Fortaleza",
            estado="CE",
            ativo=True,
        )
        unidade_recife = ModeloUnidade(
            nome="Raízes do Nordeste - Recife Boa Viagem",
            endereco="Av. Boa Viagem, 1800",
            cidade="Recife",
            estado="PE",
            ativo=True,
        )
        sessao.add_all([unidade_fortaleza, unidade_recife])
        sessao.flush()

        cuscuz_camarao = ModeloProduto(nome="Cuscuz com Camarão", descricao="Cuscuz nordestino com camarão fresco e azeite", preco=28.90, categoria="Prato Principal", ativo=True)
        tapioca_queijo = ModeloProduto(nome="Tapioca de Queijo e Tomate", descricao="Tapioca tradicional com queijo coalho e tomate", preco=14.50, categoria="Lanches", ativo=True)
        cafe_coador = ModeloProduto(nome="Café Coado Nordestino", descricao="Café passado na hora com grãos do sertão", preco=6.00, categoria="Bebidas", ativo=True)
        bolo_milho = ModeloProduto(nome="Bolo de Milho Caseiro", descricao="Bolo fubá com coco ralado", preco=9.90, categoria="Sobremesas", ativo=True)
        carne_sol = ModeloProduto(nome="Prato de Carne de Sol", descricao="Carne de sol grelhada com manteiga de garrafa e macaxeira", preco=42.00, categoria="Prato Principal", ativo=True)
        baião_dois = ModeloProduto(nome="Baião de Dois", descricao="Arroz com feijão verde, queijo coalho e carne de charque", preco=35.00, categoria="Prato Principal", ativo=True)
        sessao.add_all([cuscuz_camarao, tapioca_queijo, cafe_coador, bolo_milho, carne_sol, baião_dois])
        sessao.flush()

        itens_cardapio_fortaleza = [
            ModeloCardapioUnidade(unidade_id=unidade_fortaleza.id, produto_id=cuscuz_camarao.id, ativo=True),
            ModeloCardapioUnidade(unidade_id=unidade_fortaleza.id, produto_id=tapioca_queijo.id, ativo=True),
            ModeloCardapioUnidade(unidade_id=unidade_fortaleza.id, produto_id=cafe_coador.id, ativo=True),
            ModeloCardapioUnidade(unidade_id=unidade_fortaleza.id, produto_id=bolo_milho.id, ativo=True),
            ModeloCardapioUnidade(unidade_id=unidade_fortaleza.id, produto_id=carne_sol.id, ativo=True),
            ModeloCardapioUnidade(unidade_id=unidade_fortaleza.id, produto_id=baião_dois.id, ativo=True),
        ]
        itens_cardapio_recife = [
            ModeloCardapioUnidade(unidade_id=unidade_recife.id, produto_id=cuscuz_camarao.id, ativo=True),
            ModeloCardapioUnidade(unidade_id=unidade_recife.id, produto_id=tapioca_queijo.id, ativo=True),
            ModeloCardapioUnidade(unidade_id=unidade_recife.id, produto_id=cafe_coador.id, ativo=True),
            ModeloCardapioUnidade(unidade_id=unidade_recife.id, produto_id=carne_sol.id, ativo=True),
        ]
        sessao.add_all(itens_cardapio_fortaleza + itens_cardapio_recife)
        sessao.flush()

        estoques_fortaleza = [
            ModeloEstoque(unidade_id=unidade_fortaleza.id, produto_id=cuscuz_camarao.id, quantidade=50, minimo_alerta=10),
            ModeloEstoque(unidade_id=unidade_fortaleza.id, produto_id=tapioca_queijo.id, quantidade=80, minimo_alerta=15),
            ModeloEstoque(unidade_id=unidade_fortaleza.id, produto_id=cafe_coador.id, quantidade=200, minimo_alerta=30),
            ModeloEstoque(unidade_id=unidade_fortaleza.id, produto_id=bolo_milho.id, quantidade=30, minimo_alerta=5),
            ModeloEstoque(unidade_id=unidade_fortaleza.id, produto_id=carne_sol.id, quantidade=25, minimo_alerta=5),
            ModeloEstoque(unidade_id=unidade_fortaleza.id, produto_id=baião_dois.id, quantidade=40, minimo_alerta=8),
        ]
        estoques_recife = [
            ModeloEstoque(unidade_id=unidade_recife.id, produto_id=cuscuz_camarao.id, quantidade=1, minimo_alerta=10), # Estoque com valor 1 para testar o cenário T09 (pedido com estoque insuficiente se pedirem 2+)
            ModeloEstoque(unidade_id=unidade_recife.id, produto_id=tapioca_queijo.id, quantidade=60, minimo_alerta=10),
            ModeloEstoque(unidade_id=unidade_recife.id, produto_id=cafe_coador.id, quantidade=150, minimo_alerta=20),
            ModeloEstoque(unidade_id=unidade_recife.id, produto_id=carne_sol.id, quantidade=20, minimo_alerta=5),
        ]
        sessao.add_all(estoques_fortaleza + estoques_recife)

        sessao.commit()
        print("Banco populado com sucesso!")
        print(f"Usuários criados: {sessao.query(ModeloUsuario).count()}")
        print(f"Unidades criadas: {sessao.query(ModeloUnidade).count()}")
        print(f"Produtos criados: {sessao.query(ModeloProduto).count()}")
        print()
        print("Credenciais para teste:")
        print("admin@raizesnordeste.com.br / Admin@123")
        print("gerente@raizesnordeste.com.br / Gerente@123")
        print("cozinha@raizesnordeste.com.br / Cozinha@123")
        print("atendente@raizesnordeste.com.br / Atendente@123")
        print("cliente@raizesnordeste.com.br / Cliente@123  (com consentimento LGPD)")
        print("fernanda@email.com / Cliente@123  (sem consentimento LGPD)")

    except Exception as e:
        sessao.rollback()
        print(f"Erro ao popular banco: {e}")
        raise
    finally:
        sessao.close()

if __name__ == "__main__":
    popular_banco()
