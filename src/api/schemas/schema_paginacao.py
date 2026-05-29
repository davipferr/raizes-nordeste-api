from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class RespostaPaginada(BaseModel, Generic[T]):
    itens: list[T]
    total: int
    pagina: int
    limite: int
    paginas: int
