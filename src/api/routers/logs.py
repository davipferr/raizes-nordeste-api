from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.api.dependencias.banco import obter_db
from src.api.dependencias.autenticacao import requer_perfis
from src.api.respostas_erro import NAO_AUTENTICADO, PERMISSAO_NEGADA, ERRO_INTERNO
from src.dominio.enums import PerfilUsuario
from src.infraestrutura.banco.modelos import ModeloLogAuditoria, ModeloUsuario

roteador = APIRouter(prefix="/logs", tags=["Logs e Auditoria"])

@roteador.get(
    "/auditoria",
    summary="Consultar logs de auditoria",
    description=(
        "**Autenticação:** JWT obrigatório (`Authorization: Bearer <token>`).\n\n"
        "**Perfis permitidos:** `ADMIN`.\n\n"
        "Retorna os registros de auditoria das ações sensíveis do sistema, "
        "em ordem decrescente de data. Filtre por `acao` ou `recurso`."
    ),
    responses={**NAO_AUTENTICADO, **PERMISSAO_NEGADA, **ERRO_INTERNO},
)
def listar_logs(
    acao: str | None = Query(None, description="Filtrar por ação (ex.: PEDIDO_CRIADO, LOGIN_USUARIO)"),
    recurso: str | None = Query(None, description="Filtrar por recurso (ex.: pedidos, usuarios)"),
    limite: int = Query(20, ge=1, le=100),
    sessao: Session = Depends(obter_db),
    _: ModeloUsuario = Depends(requer_perfis(PerfilUsuario.ADMIN)),
):
    query = sessao.query(ModeloLogAuditoria).order_by(ModeloLogAuditoria.criado_em.desc())
    if acao:
        query = query.filter(ModeloLogAuditoria.acao == acao)
    if recurso:
        query = query.filter(ModeloLogAuditoria.recurso == recurso)
    logs = query.limit(limite).all()
    return [
        {
            "id": log.id,
            "usuario_id": log.usuario_id,
            "acao": log.acao,
            "recurso": log.recurso,
            "recurso_id": log.recurso_id,
            "detalhes": log.detalhes,
            "ip_origem": log.ip_origem,
            "criado_em": log.criado_em.isoformat() if log.criado_em else None,
        }
        for log in logs
    ]
