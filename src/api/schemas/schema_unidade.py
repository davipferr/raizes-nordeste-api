from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator

class RequisicaoCriarUnidade(BaseModel):
    nome: str
    endereco: str
    cidade: str
    estado: str

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, v: str) -> str:
        v = v.upper().strip()
        if len(v) != 2:
            raise ValueError("O estado deve ter exatamente 2 caracteres (ex: CE, PE, BA).")
        return v

class RequisicaoAtualizarUnidade(BaseModel):
    nome: str | None = None
    endereco: str | None = None
    cidade: str | None = None
    estado: str | None = None
    ativo: bool | None = None

class RespostaUnidade(BaseModel):
    id: int
    nome: str
    endereco: str
    cidade: str
    estado: str
    ativo: bool
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)
