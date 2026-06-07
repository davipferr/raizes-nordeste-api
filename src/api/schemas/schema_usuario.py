from datetime import datetime
from pydantic import BaseModel, ConfigDict
from src.dominio.enums import PerfilUsuario

class RespostaUsuario(BaseModel):
    id: int
    nome: str
    email: str
    perfil: PerfilUsuario
    ativo: bool
    consentimento_lgpd: bool
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)

class RequisicaoAtualizarUsuario(BaseModel):
    nome: str | None = None
    consentimento_lgpd: bool | None = None
