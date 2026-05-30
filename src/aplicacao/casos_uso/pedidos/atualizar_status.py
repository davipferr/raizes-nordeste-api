from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.infraestrutura.banco.modelos import ModeloPedido, ModeloItemPedido, ModeloEstoque
from src.infraestrutura.auditoria.servico_auditoria import registrar_acao
from src.dominio.enums import StatusPedido, PerfilUsuario, TRANSICOES_PERMITIDAS
from src.dominio.excecoes import PedidoNaoEncontrado, TransicaoStatusInvalida

def _validar_transicao_por_perfil(perfil: PerfilUsuario, novo_status: StatusPedido) -> None:
    permitidas_por_perfil = {
        PerfilUsuario.COZINHA: {StatusPedido.EM_PREPARO, StatusPedido.PRONTO},
        PerfilUsuario.ATENDENTE: {StatusPedido.ENTREGUE},
    }
    restricoes = permitidas_por_perfil.get(perfil)
    if restricoes and novo_status not in restricoes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "erro": "PERMISSAO_NEGADA",
                "mensagem": f"Perfil '{perfil.value}' não pode definir o status '{novo_status.value}'.",
                "detalhes": [],
            },
        )

def _restaurar_estoque(sessao: Session, pedido_id: int) -> None:
    itens = sessao.query(ModeloItemPedido).filter(ModeloItemPedido.pedido_id == pedido_id).all()
    for item in itens:
        pedido = sessao.query(ModeloPedido).filter(ModeloPedido.id == pedido_id).first()
        estoque = sessao.query(ModeloEstoque).filter(
            ModeloEstoque.unidade_id == pedido.unidade_id,
            ModeloEstoque.produto_id == item.produto_id,
        ).first()
        if estoque:
            estoque.quantidade += item.quantidade

def atualizar_status_pedido(
    sessao: Session,
    pedido_id: int,
    novo_status: StatusPedido,
    usuario_id: int,
    perfil: PerfilUsuario,
    motivo: str | None = None,
    ip_origem: str | None = None,
) -> ModeloPedido:
    pedido = sessao.query(ModeloPedido).filter(ModeloPedido.id == pedido_id).first()
    if not pedido:
        raise PedidoNaoEncontrado(pedido_id)

    permitidas = TRANSICOES_PERMITIDAS.get(pedido.status, [])
    if novo_status not in permitidas:
        raise TransicaoStatusInvalida(pedido.status.value, novo_status.value)

    _validar_transicao_por_perfil(perfil, novo_status)

    status_anterior = pedido.status.value
    pedido.status = novo_status

    if novo_status == StatusPedido.CANCELADO:
        _restaurar_estoque(sessao, pedido_id)
        registrar_acao(
            sessao, "PEDIDO_CANCELADO", "pedidos", str(pedido_id),
            usuario_id=usuario_id,
            detalhes={"motivo": motivo, "status_anterior": status_anterior},
            ip_origem=ip_origem,
        )

    registrar_acao(
        sessao, "STATUS_PEDIDO_ALTERADO", "pedidos", str(pedido_id),
        usuario_id=usuario_id,
        detalhes={"status_anterior": status_anterior, "novo_status": novo_status.value, "motivo": motivo},
        ip_origem=ip_origem,
    )

    sessao.commit()
    sessao.refresh(pedido)
    return pedido
