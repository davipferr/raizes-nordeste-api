from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from src.api.dependencias.banco import obter_db
from src.api.dependencias.autenticacao import requer_perfis
from src.api.schemas.schema_pagamento import RequisicaoProcessarPagamento, RespostaPagamento
from src.api.respostas_erro import (
    NAO_AUTENTICADO, PERMISSAO_NEGADA, PEDIDO_NAO_ENCONTRADO,
    PEDIDO_NAO_AGUARDANDO_PAGAMENTO, VALIDACAO, ERRO_INTERNO
)
from src.aplicacao.casos_uso.pagamento.processar_pagamento_mock import processar_pagamento
from src.dominio.enums import PerfilUsuario
from src.infraestrutura.banco.modelos import ModeloUsuario

roteador = APIRouter(prefix="/pagamentos", tags=["Pagamentos"])

_PERFIS_PAGAMENTO = (
    PerfilUsuario.ADMIN, PerfilUsuario.GERENTE,
    PerfilUsuario.ATENDENTE, PerfilUsuario.CLIENTE
)

@roteador.post(
    "/processar/{pedido_id}",
    response_model=RespostaPagamento,
    summary="Processar pagamento mock para um pedido",
    responses={**NAO_AUTENTICADO, **PERMISSAO_NEGADA, **PEDIDO_NAO_ENCONTRADO, **PEDIDO_NAO_AGUARDANDO_PAGAMENTO, **VALIDACAO, **ERRO_INTERNO},
)
def processar(
    pedido_id: int,
    dados: RequisicaoProcessarPagamento,
    request: Request,
    sessao: Session = Depends(obter_db),
    usuario: ModeloUsuario = Depends(requer_perfis(*_PERFIS_PAGAMENTO)),
):
    return processar_pagamento(
        sessao,
        pedido_id=pedido_id,
        usuario_id=usuario.id,
        forcar_recusa=dados.forcar_recusa,
        ip_origem=request.client.host if request.client else None,
    )
