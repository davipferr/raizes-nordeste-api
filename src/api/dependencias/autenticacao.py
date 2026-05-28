from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from src.api.dependencias.banco import obter_db
from src.infraestrutura.seguranca.servico_token import decodificar_token
from src.infraestrutura.banco.modelos import ModeloUsuario
from src.dominio.enums import PerfilUsuario

esquema_bearer = HTTPBearer()

_erro_nao_autenticado = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail={
        "erro": "NAO_AUTENTICADO",
        "mensagem": "Token de acesso ausente ou inválido.",
        "detalhes": [],
    },
    headers={"WWW-Authenticate": "Bearer"},
)

def obter_usuario_atual(
    credenciais: HTTPAuthorizationCredentials = Depends(esquema_bearer),
    sessao: Session = Depends(obter_db),
) -> ModeloUsuario:
    payload = decodificar_token(credenciais.credentials)
    usuario_id = payload.get("sub")
    if not usuario_id:
        raise _erro_nao_autenticado

    usuario = sessao.query(ModeloUsuario).filter(
        ModeloUsuario.id == int(usuario_id),
        ModeloUsuario.ativo == True,
    ).first()
    if not usuario:
        raise _erro_nao_autenticado
    return usuario

def requer_perfis(*perfis: PerfilUsuario):
    def verificador(usuario: ModeloUsuario = Depends(obter_usuario_atual)) -> ModeloUsuario:
        if usuario.perfil not in perfis:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "erro": "PERMISSAO_NEGADA",
                    "mensagem": f"Perfil '{usuario.perfil.value}' não tem permissão para esta ação.",
                    "detalhes": [],
                },
            )
        return usuario
    return verificador
