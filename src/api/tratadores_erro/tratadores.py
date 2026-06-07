from datetime import datetime, timezone
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from src.dominio.excecoes import ErroNegocio, EstoqueInsuficiente, CredenciaisInvalidas, TransicaoStatusInvalida

def _corpo_erro(erro: str, mensagem: str, detalhes: list, caminho: str) -> dict:
    return {
        "erro": erro,
        "mensagem": mensagem,
        "detalhes": detalhes,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "caminho": caminho,
    }

async def tratar_validacao(request: Request, exc: RequestValidationError) -> JSONResponse:
    detalhes = [
        {"campo": " -> ".join(str(l) for l in err["loc"][1:]), "problema": err["msg"]}
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=_corpo_erro("VALIDACAO_INVALIDA", "Dados da requisição inválidos.", detalhes, str(request.url.path)),
    )

async def tratar_http_exception(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    if isinstance(exc.detail, dict):
        corpo = exc.detail
        corpo.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
        corpo.setdefault("caminho", str(request.url.path))
        return JSONResponse(status_code=exc.status_code, content=corpo)

    return JSONResponse(
        status_code=exc.status_code,
        content=_corpo_erro("ERRO_HTTP", str(exc.detail), [], str(request.url.path)),
    )

async def tratar_estoque_insuficiente(request: Request, exc: EstoqueInsuficiente) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=_corpo_erro(
            exc.codigo,
            exc.mensagem,
            [{"campo": f"itens[produto_id={exc.produto_id}].quantidade", "problema": f"Disponível: {exc.disponivel}"}],
            str(request.url.path),
        ),
    )

async def tratar_transicao_invalida(request: Request, exc: TransicaoStatusInvalida) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=_corpo_erro(exc.codigo, exc.mensagem, [], str(request.url.path)),
    )

async def tratar_credenciais_invalidas(request: Request, exc: CredenciaisInvalidas) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=_corpo_erro(exc.codigo, exc.mensagem, [], str(request.url.path)),
    )

async def tratar_erro_negocio(request: Request, exc: ErroNegocio) -> JSONResponse:
    codigo_http = status.HTTP_409_CONFLICT
    if "NAO_ENCONTRADO" in exc.codigo or "NAO_ENCONTRADA" in exc.codigo or "FORA_DO_CARDAPIO" in exc.codigo:
        codigo_http = status.HTTP_404_NOT_FOUND
    elif "LGPD" in exc.codigo or "PERMISSAO" in exc.codigo:
        codigo_http = status.HTTP_403_FORBIDDEN
    return JSONResponse(
        status_code=codigo_http,
        content=_corpo_erro(exc.codigo, exc.mensagem, [], str(request.url.path)),
    )

async def tratar_excecao_generica(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_corpo_erro("ERRO_INTERNO", "Erro interno do servidor.", [], str(request.url.path)),
    )

def registrar_handlers(app):
    from fastapi.exceptions import RequestValidationError
    app.add_exception_handler(RequestValidationError, tratar_validacao)
    app.add_exception_handler(StarletteHTTPException, tratar_http_exception)
    app.add_exception_handler(EstoqueInsuficiente, tratar_estoque_insuficiente)
    app.add_exception_handler(TransicaoStatusInvalida, tratar_transicao_invalida)
    app.add_exception_handler(CredenciaisInvalidas, tratar_credenciais_invalidas)
    app.add_exception_handler(ErroNegocio, tratar_erro_negocio)
    app.add_exception_handler(Exception, tratar_excecao_generica)
