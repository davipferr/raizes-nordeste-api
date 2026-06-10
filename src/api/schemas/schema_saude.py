from pydantic import BaseModel

class RespostaSaude(BaseModel):
    status: str
    servico: str
    versao: str
