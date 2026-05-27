from datetime import datetime
from sqlalchemy import Integer, DateTime, ForeignKey, String, JSON, func
from sqlalchemy.orm import Mapped, mapped_column
from src.infraestrutura.banco.modelos.modelo_base import ModeloBase

class ModeloLogAuditoria(ModeloBase):
    __tablename__ = "logs_auditoria"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True, index=True)
    acao: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    recurso: Mapped[str] = mapped_column(String(100), nullable=False)
    recurso_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    detalhes: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ip_origem: Mapped[str | None] = mapped_column(String(45), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
