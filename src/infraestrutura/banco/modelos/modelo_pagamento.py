from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, DateTime, Numeric, ForeignKey, Enum as ColEnum, JSON, func
from sqlalchemy.orm import Mapped, mapped_column
from src.infraestrutura.banco.modelos.modelo_base import ModeloBase
from src.dominio.enums import StatusPagamento

class ModeloPagamento(ModeloBase):
    __tablename__ = "pagamentos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id"), nullable=False, unique=True, index=True)
    valor: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    forma_pagamento: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[StatusPagamento] = mapped_column(
        ColEnum(StatusPagamento, name="status_pagamento"),
        nullable=False,
        default=StatusPagamento.PENDENTE,
    )
    payload_requisicao: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    payload_resposta: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
