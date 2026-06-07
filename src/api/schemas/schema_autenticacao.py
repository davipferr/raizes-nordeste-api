from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from src.dominio.enums import PerfilUsuario

class RequisicaoLogin(BaseModel):
    email: EmailStr
    senha: str

class RequisicaoRegistro(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    perfil: PerfilUsuario = PerfilUsuario.CLIENTE
    consentimento_lgpd: bool = False

    @field_validator("senha")
    @classmethod
    def validar_senha(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("A senha deve ter no mínimo 8 caracteres.")
        return v

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("O nome não pode ser vazio.")
        return v.strip()

class RespostaUsuarioPublico(BaseModel):
    id: int
    nome: str
    email: str
    perfil: PerfilUsuario
    consentimento_lgpd: bool

    model_config = ConfigDict(from_attributes=True)

class RespostaLogin(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    usuario: RespostaUsuarioPublico
