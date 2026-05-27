from datetime import datetime
from sqlalchemy import Integer, DateTime, ForeignKey, String, Enum as ColEnum, func
from sqlalchemy.orm import Mapped, mapped_column
from src.infraestrutura.banco.modelos.modelo_base import ModeloBase
from src.dominio.enums import TipoTransacaoFidelidade

class ModeloPontosFidelidade(ModeloBase):
    __tablename__ = "pontos_fidelidade"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False, unique=True, index=True)
    saldo: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

class ModeloTransacaoFidelidade(ModeloBase):
    __tablename__ = "transacoes_fidelidade"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False, index=True)
    pedido_id: Mapped[int | None] = mapped_column(ForeignKey("pedidos.id"), nullable=True)
    pontos: Mapped[int] = mapped_column(Integer, nullable=False)
    tipo: Mapped[TipoTransacaoFidelidade] = mapped_column(
        ColEnum(TipoTransacaoFidelidade, name="tipo_transacao_fidelidade"), nullable=False
    )
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
