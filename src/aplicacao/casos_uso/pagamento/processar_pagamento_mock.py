from sqlalchemy.orm import Session
from src.infraestrutura.banco.modelos import (
    ModeloPedido, ModeloPagamento, ModeloItemPedido, ModeloEstoque,
    ModeloPontosFidelidade, ModeloTransacaoFidelidade, ModeloUsuario
)
from src.infraestrutura.pagamento_mock.servico_pagamento_mock import simular_gateway
from src.infraestrutura.auditoria.servico_auditoria import registrar_acao
from src.dominio.enums import StatusPedido, StatusPagamento, TipoTransacaoFidelidade
from src.dominio.excecoes import PedidoNaoEncontrado, PedidoNaoAguardandoPagamento

def _restaurar_estoque_pedido(sessao: Session, pedido: ModeloPedido) -> None:
    itens = sessao.query(ModeloItemPedido).filter(ModeloItemPedido.pedido_id == pedido.id).all()
    for item in itens:
        estoque = sessao.query(ModeloEstoque).filter(
            ModeloEstoque.unidade_id == pedido.unidade_id,
            ModeloEstoque.produto_id == item.produto_id,
        ).first()
        if estoque:
            estoque.quantidade += item.quantidade

def _creditar_pontos(sessao: Session, cliente_id: int, pedido_id: int, valor_total) -> None:
    cliente = sessao.query(ModeloUsuario).filter(ModeloUsuario.id == cliente_id).first()
    if not cliente or not cliente.consentimento_lgpd:
        return

    pontos_ganhos = int(valor_total)
    if pontos_ganhos <= 0:
        return

    saldo = sessao.query(ModeloPontosFidelidade).filter(
        ModeloPontosFidelidade.cliente_id == cliente_id
    ).first()

    if saldo:
        saldo.saldo += pontos_ganhos
    else:
        saldo = ModeloPontosFidelidade(cliente_id=cliente_id, saldo=pontos_ganhos)
        sessao.add(saldo)

    sessao.add(ModeloTransacaoFidelidade(
        cliente_id=cliente_id,
        pedido_id=pedido_id,
        pontos=pontos_ganhos,
        tipo=TipoTransacaoFidelidade.GANHO,
        descricao=f"Pontos ganhos no pedido #{pedido_id}",
    ))

def processar_pagamento(
    sessao: Session,
    pedido_id: int,
    usuario_id: int,
    forcar_recusa: bool = False,
    ip_origem: str | None = None,
) -> dict:
    pedido = sessao.query(ModeloPedido).filter(ModeloPedido.id == pedido_id).first()
    if not pedido:
        raise PedidoNaoEncontrado(pedido_id)
    if pedido.status != StatusPedido.AGUARDANDO_PAGAMENTO:
        raise PedidoNaoAguardandoPagamento(pedido_id, pedido.status.value)

    aprovado, payload_req, payload_resp = simular_gateway(
        pedido_id=pedido.id,
        valor=pedido.total,
        forma_pagamento=pedido.forma_pagamento,
        forcar_recusa=forcar_recusa,
    )

    status_pagamento = StatusPagamento.APROVADO if aprovado else StatusPagamento.RECUSADO
    pagamento = ModeloPagamento(
        pedido_id=pedido.id,
        valor=pedido.total,
        forma_pagamento=pedido.forma_pagamento,
        status=status_pagamento,
        payload_requisicao=payload_req,
        payload_resposta=payload_resp,
    )
    sessao.add(pagamento)

    if aprovado:
        pedido.status = StatusPedido.PAGAMENTO_APROVADO
        _creditar_pontos(sessao, pedido.cliente_id, pedido.id, pedido.total)
        registrar_acao(
            sessao, "PAGAMENTO_APROVADO", "pagamentos", str(pedido.id),
            usuario_id=usuario_id,
            detalhes={"valor": str(pedido.total), "transacao_id": payload_resp.get("transacao_id")},
            ip_origem=ip_origem,
        )
    else:
        _restaurar_estoque_pedido(sessao, pedido)
        pedido.status = StatusPedido.CANCELADO
        registrar_acao(
            sessao, "PAGAMENTO_RECUSADO", "pagamentos", str(pedido.id),
            usuario_id=usuario_id,
            detalhes={"valor": str(pedido.total), "codigo": payload_resp.get("codigo_resposta")},
            ip_origem=ip_origem,
        )

    sessao.commit()
    sessao.refresh(pagamento)

    return {
        "pedido_id": pedido.id,
        "valor": pedido.total,
        "forma_pagamento": pedido.forma_pagamento,
        "status": status_pagamento,
        "aprovado": aprovado,
        "mensagem": payload_resp["mensagem"],
        "payload_gateway": payload_resp,
        "criado_em": pagamento.criado_em,
    }
