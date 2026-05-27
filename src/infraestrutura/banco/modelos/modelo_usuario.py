from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Enum as ColEnum, func
from sqlalchemy.orm import Mapped, mapped_column
from src.infraestrutura.banco.modelos.modelo_base import ModeloBase
from src.dominio.enums import PerfilUsuario

class ModeloUsuario(ModeloBase):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    perfil: Mapped[PerfilUsuario] = mapped_column(
        ColEnum(PerfilUsuario, name="perfil_usuario"), nullable=False, default=PerfilUsuario.CLIENTE
    )
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    consentimento_lgpd: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    data_consentimento: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
