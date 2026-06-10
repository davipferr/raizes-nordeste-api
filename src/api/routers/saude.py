from fastapi import APIRouter
from src.api.schemas.schema_saude import RespostaSaude
from src.api.respostas_erro import ERRO_INTERNO

roteador = APIRouter(prefix="/saude", tags=["Saúde"])

@roteador.get("", response_model=RespostaSaude, summary="Verificar saúde da API",
              description=(
                  "**Autenticação:** Pública — não requer token JWT.\n\n"
                  "Retorna o status operacional da API, o nome do serviço e a versão atual."
              ),
              responses={**ERRO_INTERNO})
def verificar_saude():
    return RespostaSaude(
        status="online",
        servico="API Raízes do Nordeste",
        versao="1.0.0",
    )
