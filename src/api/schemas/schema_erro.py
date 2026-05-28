from datetime import datetime, timezone
from pydantic import BaseModel

class DetalheErro(BaseModel):
    campo: str | None = None
    problema: str

class RespostaErro(BaseModel):
    erro: str
    mensagem: str
    detalhes: list[DetalheErro] = []
    timestamp: str = ""
    caminho: str = ""
    requisicao_id: str | None = None

    @classmethod
    def criar(
        cls,
        erro: str,
        mensagem: str,
        detalhes: list[DetalheErro] | None = None,
        caminho: str = "",
        requisicao_id: str | None = None,
    ) -> "RespostaErro":
        return cls(
            erro=erro,
            mensagem=mensagem,
            detalhes=detalhes or [],
            timestamp=datetime.now(timezone.utc).isoformat(),
            caminho=caminho,
            requisicao_id=requisicao_id,
        )
