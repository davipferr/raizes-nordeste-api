from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.api.dependencias.banco import obter_db
from src.api.dependencias.autenticacao import obter_usuario_atual
from src.api.schemas.schema_usuario import RespostaUsuario, RequisicaoAtualizarUsuario
from src.api.respostas_erro import (
    NAO_AUTENTICADO, PERMISSAO_NEGADA, USUARIO_NAO_ENCONTRADO, VALIDACAO, ERRO_INTERNO
)
from src.infraestrutura.banco.modelos import ModeloUsuario

roteador = APIRouter(prefix="/usuarios", tags=["Usuários"])

@roteador.get("/me", response_model=RespostaUsuario, summary="Perfil do usuário atual",
              responses={**NAO_AUTENTICADO, **ERRO_INTERNO})
def obter_perfil(usuario: ModeloUsuario = Depends(obter_usuario_atual)):
    return usuario

@roteador.put("/me", response_model=RespostaUsuario, summary="Atualizar perfil do usuário atual",
              responses={**NAO_AUTENTICADO, **VALIDACAO, **ERRO_INTERNO})
def atualizar_perfil(
    dados: RequisicaoAtualizarUsuario,
    sessao: Session = Depends(obter_db),
    usuario: ModeloUsuario = Depends(obter_usuario_atual),
):
    if dados.nome is not None:
        usuario.nome = dados.nome.strip()
    if dados.consentimento_lgpd is not None:
        usuario.consentimento_lgpd = dados.consentimento_lgpd
        if dados.consentimento_lgpd:
            usuario.data_consentimento = datetime.now(timezone.utc)
    sessao.commit()
    sessao.refresh(usuario)
    return usuario

@roteador.get("/{usuario_id}", response_model=RespostaUsuario, summary="Buscar usuário por ID",
              responses={**NAO_AUTENTICADO, **PERMISSAO_NEGADA, **USUARIO_NAO_ENCONTRADO, **ERRO_INTERNO})
def obter_usuario(
    usuario_id: int,
    sessao: Session = Depends(obter_db),
    usuario_atual: ModeloUsuario = Depends(obter_usuario_atual),
):
    from src.dominio.enums import PerfilUsuario
    if usuario_atual.id != usuario_id and usuario_atual.perfil not in [PerfilUsuario.ADMIN, PerfilUsuario.GERENTE]:
        raise HTTPException(status_code=403, detail={
            "erro": "PERMISSAO_NEGADA",
            "mensagem": "Você não tem permissão para visualizar este usuário.",
            "detalhes": [],
        })
    usuario = sessao.query(ModeloUsuario).filter(ModeloUsuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail={
            "erro": "USUARIO_NAO_ENCONTRADO",
            "mensagem": f"Usuário {usuario_id} não encontrado.",
            "detalhes": [],
        })
    return usuario
