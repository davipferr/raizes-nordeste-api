from sqlalchemy import ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from src.infraestrutura.banco.modelos.modelo_base import ModeloBase

class ModeloCardapioUnidade(ModeloBase):
    __tablename__ = "cardapio_unidade"
    __table_args__ = (UniqueConstraint("unidade_id", "produto_id", name="uq_cardapio_unidade_produto"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    unidade_id: Mapped[int] = mapped_column(ForeignKey("unidades.id"), nullable=False, index=True)
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id"), nullable=False, index=True)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
