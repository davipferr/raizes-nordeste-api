from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

_CONTACT = {"name": "Raízes do Nordeste", "email": "ti@raizesnordeste.com.br"}

_TAGS = [
    {"name": "Autenticação", "description": "Login e registro de usuários"},
    {"name": "Usuários", "description": "Gerenciamento de usuários"},
    {"name": "Unidades", "description": "Unidades da rede"},
    {"name": "Produtos", "description": "Catálogo de produtos"},
    {"name": "Cardápio", "description": "Cardápio por unidade"},
    {"name": "Estoque", "description": "Controle de estoque por unidade"},
    {"name": "Pedidos", "description": "Gestão de pedidos multicanal"},
    {"name": "Pagamentos", "description": "Processamento de pagamento (mock)"},
    {"name": "Fidelidade", "description": "Programa de pontos e fidelização"},
]

_SCHEMA_RESPOSTA_ERRO = {
    "title": "RespostaErro",
    "type": "object",
    "required": ["erro", "mensagem"],
    "properties": {
        "erro": {"title": "Código do erro", "type": "string", "example": "VALIDACAO_INVALIDA"},
        "mensagem": {"title": "Mensagem", "type": "string", "example": "Dados da requisição inválidos."},
        "detalhes": {
            "title": "Detalhes",
            "type": "array",
            "default": [],
            "items": {
                "title": "DetalheErro",
                "type": "object",
                "required": ["problema"],
                "properties": {
                    "campo": {"title": "Campo", "anyOf": [{"type": "string"}, {"type": "null"}]},
                    "problema": {"title": "Problema", "type": "string"},
                },
            },
        },
        "timestamp": {"title": "Timestamp", "type": "string", "example": "2026-06-04T12:00:00+00:00"},
        "caminho": {"title": "Caminho", "type": "string", "example": "/autenticacao/login"},
        "requisicao_id": {"title": "ID da requisição", "anyOf": [{"type": "string"}, {"type": "null"}]},
    },
}


def criar_app() -> FastAPI:
    app = FastAPI(
        title="API Raízes do Nordeste",
        description=(
            "Sistema de gestão para a rede de lanchonetes Raízes do Nordeste. "
            "Suporte a múltiplos canais (APP, TOTEM, BALCÃO, PICKUP, WEB), "
            "controle de estoque por unidade, programa de fidelidade e pagamento mock."
        ),
        version="1.0.0",
        contact=_CONTACT,
        openapi_tags=_TAGS,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    def _openapi():
        if app.openapi_schema:
            return app.openapi_schema
        schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            contact=_CONTACT,
            tags=_TAGS,
            routes=app.routes,
        )
        schemas = schema.get("components", {}).get("schemas", {})
        schemas.pop("ValidationError", None)
        if "HTTPValidationError" in schemas:
            schemas["HTTPValidationError"] = _SCHEMA_RESPOSTA_ERRO

        schemas["RespostaErro"] = _SCHEMA_RESPOSTA_ERRO
        app.openapi_schema = schema
        return schema

    app.openapi = _openapi
    return app
