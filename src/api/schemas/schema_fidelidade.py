from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator
from src.dominio.enums import TipoTransacaoFidelidade

class RespostaSaldoFidelidade(BaseModel):
    cliente_id: int
    saldo: int
    equivalente_reais: float

class RequisicaoResgatarPontos(BaseModel):
    pontos: int

    @field_validator("pontos")
    @classmethod
    def validar_pontos(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("A quantidade de pontos deve ser positiva.")
        return v

class RespostaResgate(BaseModel):
    pontos_resgatados: int
    desconto_reais: float
    saldo_restante: int

class RespostaTransacaoFidelidade(BaseModel):
    id: int
    pontos: int
    tipo: TipoTransacaoFidelidade
    descricao: str
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)
