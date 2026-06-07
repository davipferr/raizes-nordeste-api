from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from src.api.configuracao import criar_app
from src.api.tratadores_erro.tratadores import registrar_handlers
from src.api.middleware.log_requisicoes import middleware_log
from src.api.routers import (
    autenticacao, usuarios, unidades, produtos,
    cardapio, estoque, pedidos, pagamentos, fidelidade, logs
)

app: FastAPI = criar_app()

registrar_handlers(app)
app.add_middleware(BaseHTTPMiddleware, dispatch=middleware_log)

app.include_router(autenticacao.roteador)
app.include_router(usuarios.roteador)
app.include_router(unidades.roteador)
app.include_router(produtos.roteador)
app.include_router(cardapio.roteador)
app.include_router(estoque.roteador)
app.include_router(pedidos.roteador)
app.include_router(pagamentos.roteador)
app.include_router(fidelidade.roteador)
app.include_router(logs.roteador)

@app.get("/", tags=["Saúde"])
def verificar_saude():
    return {"status": "online", "servico": "API Raízes do Nordeste", "versao": "1.0.0"}
