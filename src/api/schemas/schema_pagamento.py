from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from src.dominio.enums import StatusPagamento

class RequisicaoProcessarPagamento(BaseModel):
    forcar_recusa: bool = False

class RespostaPagamento(BaseModel):
    pedido_id: int
    valor: Decimal
    forma_pagamento: str
    status: StatusPagamento
    aprovado: bool
    mensagem: str
    payload_gateway: dict
    criado_em: datetime
