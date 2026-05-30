from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, field_validator
from src.dominio.enums import CanalPedido, StatusPedido

class ItemPedidoRequisicao(BaseModel):
    produto_id: int
    quantidade: int

    @field_validator("quantidade")
    @classmethod
    def validar_quantidade(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")
        return v

class RequisicaoCriarPedido(BaseModel):
    unidade_id: int
    canal_pedido: CanalPedido
    itens: list[ItemPedidoRequisicao]
    forma_pagamento: str
    observacoes: str | None = None

    @field_validator("itens")
    @classmethod
    def validar_itens(cls, v: list) -> list:
        if not v:
            raise ValueError("O pedido deve conter ao menos um item.")
        return v

    @field_validator("forma_pagamento")
    @classmethod
    def validar_forma_pagamento(cls, v: str) -> str:
        formas_validas = {"PIX", "CARTAO_CREDITO", "CARTAO_DEBITO", "DINHEIRO", "MOCK"}
        if v.upper() not in formas_validas:
            raise ValueError(f"Forma de pagamento inválida. Use: {', '.join(formas_validas)}")
        return v.upper()

class RequisicaoAtualizarStatus(BaseModel):
    status: StatusPedido
    motivo: str | None = None

class ItemPedidoResposta(BaseModel):
    produto_id: int
    produto_nome: str
    quantidade: int
    preco_unitario: Decimal
    subtotal: Decimal

class RespostaPedido(BaseModel):
    id: int
    unidade_id: int
    cliente_id: int
    canal_pedido: CanalPedido
    status: StatusPedido
    total: Decimal
    forma_pagamento: str
    observacoes: str | None
    itens: list[ItemPedidoResposta]
    criado_em: datetime
    atualizado_em: datetime

class RespostaPedidoResumo(BaseModel):
    id: int
    unidade_id: int
    cliente_id: int
    canal_pedido: CanalPedido
    status: StatusPedido
    total: Decimal
    forma_pagamento: str
    criado_em: datetime
