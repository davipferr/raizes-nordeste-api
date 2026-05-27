import enum

class StatusPedido(str, enum.Enum):
    AGUARDANDO_PAGAMENTO = "AGUARDANDO_PAGAMENTO"
    PAGAMENTO_APROVADO = "PAGAMENTO_APROVADO"
    EM_PREPARO = "EM_PREPARO"
    PRONTO = "PRONTO"
    ENTREGUE = "ENTREGUE"
    CANCELADO = "CANCELADO"

TRANSICOES_PERMITIDAS: dict[StatusPedido, list[StatusPedido]] = {
    StatusPedido.AGUARDANDO_PAGAMENTO: [StatusPedido.PAGAMENTO_APROVADO, StatusPedido.CANCELADO],
    StatusPedido.PAGAMENTO_APROVADO: [StatusPedido.EM_PREPARO, StatusPedido.CANCELADO],
    StatusPedido.EM_PREPARO: [StatusPedido.PRONTO, StatusPedido.CANCELADO],
    StatusPedido.PRONTO: [StatusPedido.ENTREGUE, StatusPedido.CANCELADO],
    StatusPedido.ENTREGUE: [],
    StatusPedido.CANCELADO: [],
}
