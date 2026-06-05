import math
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from src.api.dependencias.banco import obter_db
from src.api.dependencias.autenticacao import obter_usuario_atual, requer_perfis
from src.api.schemas.schema_pedido import (
    RequisicaoCriarPedido, RequisicaoAtualizarStatus,
    RespostaPedido, RespostaPedidoResumo
)
from src.api.schemas.schema_paginacao import RespostaPaginada
from src.api.respostas_erro import (
    NAO_AUTENTICADO, PERMISSAO_NEGADA, PEDIDO_NAO_ENCONTRADO,
    RECURSOS_PEDIDO_NAO_ENCONTRADO, ESTOQUE_INSUFICIENTE,
    TRANSICAO_STATUS_INVALIDA, VALIDACAO, ERRO_INTERNO
)
from src.aplicacao.casos_uso.pedidos.criar_pedido import criar_pedido
from src.aplicacao.casos_uso.pedidos.listar_pedidos import listar_pedidos, obter_pedido_com_itens
from src.aplicacao.casos_uso.pedidos.atualizar_status import atualizar_status_pedido
from src.dominio.enums import CanalPedido, StatusPedido, PerfilUsuario
from src.infraestrutura.banco.modelos import ModeloUsuario

roteador = APIRouter(prefix="/pedidos", tags=["Pedidos"])

_PERFIS_PEDIDO = (
    PerfilUsuario.ADMIN, PerfilUsuario.GERENTE,
    PerfilUsuario.ATENDENTE, PerfilUsuario.CLIENTE
)
_PERFIS_STATUS = (
    PerfilUsuario.ADMIN, PerfilUsuario.GERENTE,
    PerfilUsuario.COZINHA, PerfilUsuario.ATENDENTE
)

@roteador.post("", response_model=RespostaPedido, status_code=201, summary="Criar pedido",
               responses={**NAO_AUTENTICADO, **PERMISSAO_NEGADA, **RECURSOS_PEDIDO_NAO_ENCONTRADO, **ESTOQUE_INSUFICIENTE, **VALIDACAO, **ERRO_INTERNO})
def criar(
    dados: RequisicaoCriarPedido,
    request: Request,
    sessao: Session = Depends(obter_db),
    usuario: ModeloUsuario = Depends(requer_perfis(*_PERFIS_PEDIDO)),
):
    pedido = criar_pedido(
        sessao,
        unidade_id=dados.unidade_id,
        cliente_id=usuario.id,
        canal_pedido=dados.canal_pedido,
        itens=[{"produto_id": i.produto_id, "quantidade": i.quantidade} for i in dados.itens],
        forma_pagamento=dados.forma_pagamento,
        observacoes=dados.observacoes,
        ip_origem=request.client.host if request.client else None,
    )
    return obter_pedido_com_itens(sessao, pedido.id)

@roteador.get("", response_model=RespostaPaginada[RespostaPedidoResumo], summary="Listar pedidos",
              responses={**NAO_AUTENTICADO, **ERRO_INTERNO})
def listar(
    pagina: int = Query(1, ge=1),
    limite: int = Query(10, ge=1, le=100),
    canal_pedido: CanalPedido | None = Query(None, alias="canalPedido"),
    status: StatusPedido | None = Query(None),
    unidade_id: int | None = Query(None),
    sessao: Session = Depends(obter_db),
    usuario: ModeloUsuario = Depends(obter_usuario_atual),
):
    cliente_id_filtro = None
    if usuario.perfil == PerfilUsuario.CLIENTE:
        cliente_id_filtro = usuario.id

    pedidos, total = listar_pedidos(
        sessao, pagina, limite, canal_pedido, status, unidade_id, cliente_id_filtro
    )
    return RespostaPaginada(
        itens=pedidos, total=total, pagina=pagina,
        limite=limite, paginas=math.ceil(total / limite) or 1
    )

@roteador.get("/{pedido_id}", response_model=RespostaPedido, summary="Obter pedido com itens",
              responses={**NAO_AUTENTICADO, **PERMISSAO_NEGADA, **PEDIDO_NAO_ENCONTRADO, **ERRO_INTERNO})
def obter(
    pedido_id: int,
    sessao: Session = Depends(obter_db),
    usuario: ModeloUsuario = Depends(obter_usuario_atual),
):
    dados = obter_pedido_com_itens(sessao, pedido_id)
    if usuario.perfil == PerfilUsuario.CLIENTE and dados["cliente_id"] != usuario.id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail={
            "erro": "PERMISSAO_NEGADA",
            "mensagem": "Você só pode visualizar seus próprios pedidos.",
            "detalhes": [],
        })
    return dados

@roteador.patch("/{pedido_id}/status", response_model=RespostaPedido, summary="Atualizar status do pedido",
                responses={**NAO_AUTENTICADO, **PERMISSAO_NEGADA, **PEDIDO_NAO_ENCONTRADO, **TRANSICAO_STATUS_INVALIDA, **VALIDACAO, **ERRO_INTERNO})
def atualizar_status(
    pedido_id: int,
    dados: RequisicaoAtualizarStatus,
    request: Request,
    sessao: Session = Depends(obter_db),
    usuario: ModeloUsuario = Depends(requer_perfis(*_PERFIS_STATUS)),
):
    pedido = atualizar_status_pedido(
        sessao,
        pedido_id=pedido_id,
        novo_status=dados.status,
        usuario_id=usuario.id,
        perfil=usuario.perfil,
        motivo=dados.motivo,
        ip_origem=request.client.host if request.client else None,
    )
    return obter_pedido_com_itens(sessao, pedido.id)
