from datetime import datetime
from sqlalchemy import ForeignKey, Integer, DateTime, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from src.infraestrutura.banco.modelos.modelo_base import ModeloBase

class ModeloEstoque(ModeloBase):
    __tablename__ = "estoque"
    __table_args__ = (UniqueConstraint("unidade_id", "produto_id", name="uq_estoque_unidade_produto"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    unidade_id: Mapped[int] = mapped_column(ForeignKey("unidades.id"), nullable=False, index=True)
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id"), nullable=False, index=True)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    minimo_alerta: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
