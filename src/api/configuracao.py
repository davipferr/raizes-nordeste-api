from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def criar_app() -> FastAPI:
    app = FastAPI(
        title="API Raízes do Nordeste",
        description=(
            "Sistema de gestão para a rede de lanchonetes Raízes do Nordeste. "
            "Suporte a múltiplos canais (APP, TOTEM, BALCÃO, PICKUP, WEB), "
            "controle de estoque por unidade, programa de fidelidade e pagamento mock."
        ),
        version="1.0.0",
        contact={"name": "Raízes do Nordeste", "email": "ti@raizesnordeste.com.br"},
        openapi_tags=[
            {"name": "Autenticação", "description": "Login e registro de usuários"},
            {"name": "Usuários", "description": "Gerenciamento de usuários"},
            {"name": "Unidades", "description": "Unidades da rede"},
            {"name": "Produtos", "description": "Catálogo de produtos"},
            {"name": "Cardápio", "description": "Cardápio por unidade"},
            {"name": "Estoque", "description": "Controle de estoque por unidade"},
            {"name": "Pedidos", "description": "Gestão de pedidos multicanal"},
            {"name": "Pagamentos", "description": "Processamento de pagamento (mock)"},
            {"name": "Fidelidade", "description": "Programa de pontos e fidelização"},
        ],
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app
