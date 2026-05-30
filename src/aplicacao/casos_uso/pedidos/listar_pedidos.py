from sqlalchemy.orm import Session
from src.infraestrutura.banco.modelos import ModeloPedido, ModeloItemPedido, ModeloProduto
from src.dominio.enums import CanalPedido, StatusPedido
from src.dominio.excecoes import PedidoNaoEncontrado

def listar_pedidos(
    sessao: Session,
    pagina: int,
    limite: int,
    canal_pedido: CanalPedido | None = None,
    status: StatusPedido | None = None,
    unidade_id: int | None = None,
    cliente_id: int | None = None,
):
    consulta = sessao.query(ModeloPedido)
    if canal_pedido:
        consulta = consulta.filter(ModeloPedido.canal_pedido == canal_pedido)
    if status:
        consulta = consulta.filter(ModeloPedido.status == status)
    if unidade_id:
        consulta = consulta.filter(ModeloPedido.unidade_id == unidade_id)
    if cliente_id:
        consulta = consulta.filter(ModeloPedido.cliente_id == cliente_id)

    total = consulta.count()
    pedidos = consulta.order_by(ModeloPedido.criado_em.desc()).offset((pagina - 1) * limite).limit(limite).all()
    return pedidos, total

def obter_pedido_com_itens(sessao: Session, pedido_id: int) -> dict:
    pedido = sessao.query(ModeloPedido).filter(ModeloPedido.id == pedido_id).first()
    if not pedido:
        raise PedidoNaoEncontrado(pedido_id)

    itens_raw = (
        sessao.query(ModeloItemPedido, ModeloProduto)
        .join(ModeloProduto, ModeloProduto.id == ModeloItemPedido.produto_id)
        .filter(ModeloItemPedido.pedido_id == pedido_id)
        .all()
    )

    itens = [
        {
            "produto_id": item.produto_id,
            "produto_nome": prod.nome,
            "quantidade": item.quantidade,
            "preco_unitario": item.preco_unitario,
            "subtotal": item.preco_unitario * item.quantidade,
        }
        for item, prod in itens_raw
    ]

    return {
        "id": pedido.id,
        "unidade_id": pedido.unidade_id,
        "cliente_id": pedido.cliente_id,
        "canal_pedido": pedido.canal_pedido,
        "status": pedido.status,
        "total": pedido.total,
        "forma_pagamento": pedido.forma_pagamento,
        "observacoes": pedido.observacoes,
        "itens": itens,
        "criado_em": pedido.criado_em,
        "atualizado_em": pedido.atualizado_em,
    }
