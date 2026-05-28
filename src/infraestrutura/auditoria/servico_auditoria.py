from sqlalchemy.orm import Session
from src.infraestrutura.banco.modelos import ModeloLogAuditoria

def registrar_acao(
    sessao: Session,
    acao: str,
    recurso: str,
    recurso_id: str | None = None,
    usuario_id: int | None = None,
    detalhes: dict | None = None,
    ip_origem: str | None = None,
) -> None:
    log = ModeloLogAuditoria(
        usuario_id=usuario_id,
        acao=acao,
        recurso=recurso,
        recurso_id=str(recurso_id) if recurso_id is not None else None,
        detalhes=detalhes,
        ip_origem=ip_origem,
    )
    sessao.add(log)
