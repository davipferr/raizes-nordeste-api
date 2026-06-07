from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, field_validator

class RequisicaoCriarProduto(BaseModel):
    nome: str
    descricao: str | None = None
    preco: Decimal
    categoria: str

    @field_validator("preco")
    @classmethod
    def validar_preco(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("O preço deve ser maior que zero.")
        return v

class RequisicaoAtualizarProduto(BaseModel):
    nome: str | None = None
    descricao: str | None = None
    preco: Decimal | None = None
    categoria: str | None = None
    ativo: bool | None = None

class RespostaProduto(BaseModel):
    id: int
    nome: str
    descricao: str | None
    preco: Decimal
    categoria: str
    ativo: bool
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)

class RespostaProdutoCardapio(BaseModel):
    id: int
    nome: str
    descricao: str | None
    preco: Decimal
    categoria: str

    model_config = ConfigDict(from_attributes=True)
