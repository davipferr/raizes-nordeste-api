from datetime import datetime
from pydantic import BaseModel, field_validator

class RequisicaoMovimentacaoEstoque(BaseModel):
    unidade_id: int
    produto_id: int
    quantidade: int
    motivo: str | None = None

    @field_validator("quantidade")
    @classmethod
    def validar_quantidade(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")
        return v

class RespostaEstoque(BaseModel):
    produto_id: int
    produto_nome: str
    unidade_id: int
    quantidade: int
    minimo_alerta: int
    em_alerta: bool
    atualizado_em: datetime
