import math
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from src.api.dependencias.banco import obter_db
from src.api.dependencias.autenticacao import obter_usuario_atual
from src.api.schemas.schema_fidelidade import (
    RespostaSaldoFidelidade, RequisicaoResgatarPontos,
    RespostaResgate, RespostaTransacaoFidelidade
)
from src.api.schemas.schema_paginacao import RespostaPaginada
from src.api.respostas_erro import (
    NAO_AUTENTICADO, CONSENTIMENTO_LGPD, SALDO_INSUFICIENTE, VALIDACAO, ERRO_INTERNO
)
from src.aplicacao.casos_uso.fidelidade.consultar_saldo import consultar_saldo, consultar_historico
from src.aplicacao.casos_uso.fidelidade.resgatar_pontos import resgatar_pontos
from src.infraestrutura.banco.modelos import ModeloUsuario

roteador = APIRouter(prefix="/fidelidade", tags=["Fidelidade"])

@roteador.get("/saldo", response_model=RespostaSaldoFidelidade, summary="Consultar saldo de pontos",
              responses={**NAO_AUTENTICADO, **CONSENTIMENTO_LGPD, **ERRO_INTERNO})
def saldo(
    sessao: Session = Depends(obter_db),
    usuario: ModeloUsuario = Depends(obter_usuario_atual),
):
    return consultar_saldo(sessao, usuario.id)

@roteador.get(
    "/historico",
    response_model=RespostaPaginada[RespostaTransacaoFidelidade],
    summary="Histórico de transações de fidelidade",
    responses={**NAO_AUTENTICADO, **CONSENTIMENTO_LGPD, **ERRO_INTERNO},
)
def historico(
    pagina: int = Query(1, ge=1),
    limite: int = Query(10, ge=1, le=50),
    sessao: Session = Depends(obter_db),
    usuario: ModeloUsuario = Depends(obter_usuario_atual),
):
    itens, total = consultar_historico(sessao, usuario.id, pagina, limite)
    return RespostaPaginada(
        itens=itens, total=total, pagina=pagina,
        limite=limite, paginas=math.ceil(total / limite) or 1
    )

@roteador.post("/resgatar", response_model=RespostaResgate, summary="Resgatar pontos de fidelidade",
               responses={**NAO_AUTENTICADO, **CONSENTIMENTO_LGPD, **SALDO_INSUFICIENTE, **VALIDACAO, **ERRO_INTERNO})
def resgatar(
    dados: RequisicaoResgatarPontos,
    request: Request,
    sessao: Session = Depends(obter_db),
    usuario: ModeloUsuario = Depends(obter_usuario_atual),
):
    return resgatar_pontos(
        sessao,
        cliente_id=usuario.id,
        pontos=dados.pontos,
        ip_origem=request.client.host if request.client else None,
    )
