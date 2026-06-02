import time
import logging
from fastapi import Request

logger = logging.getLogger("raizes_nordeste")
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

_ROTAS_SENSIVEIS = {"/auth/login", "/auth/registrar", "/pedidos", "/pagamentos", "/fidelidade"}

async def middleware_log(request: Request, call_next):
    inicio = time.time()
    resposta = await call_next(request)
    duracao_ms = round((time.time() - inicio) * 1000, 2)

    rota_base = "/" + request.url.path.lstrip("/").split("/")[0]
    if any(request.url.path.startswith(r) for r in _ROTAS_SENSIVEIS):
        logger.info(
            "[%s] %s %s | status=%s | %sms | ip=%s",
            rota_base,  # Agrupa por rota base
            request.method,
            request.url.path,
            resposta.status_code,
            duracao_ms,
            request.client.host if request.client else "desconhecido",
        )

    return resposta
