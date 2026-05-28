from datetime import datetime, timezone
from sqlalchemy.orm import Session
from src.infraestrutura.banco.modelos import ModeloUsuario
from src.infraestrutura.seguranca.servico_senha import gerar_hash
from src.dominio.enums import PerfilUsuario

def registrar_usuario(
    sessao: Session,
    nome: str,
    email: str,
    senha: str,
    perfil: PerfilUsuario = PerfilUsuario.CLIENTE,
    consentimento_lgpd: bool = False,
) -> ModeloUsuario:
    email_lower = email.lower().strip()
    existente = sessao.query(ModeloUsuario).filter(ModeloUsuario.email == email_lower).first()
    if existente:
        from fastapi import HTTPException
        raise HTTPException(status_code=409, detail={
            "erro": "EMAIL_JA_CADASTRADO",
            "mensagem": "Já existe um usuário com este e-mail.",
        })

    novo_usuario = ModeloUsuario(
        nome=nome.strip(),
        email=email_lower,
        senha_hash=gerar_hash(senha),
        perfil=perfil,
        ativo=True,
        consentimento_lgpd=consentimento_lgpd,
        data_consentimento=datetime.now(timezone.utc) if consentimento_lgpd else None,
    )
    sessao.add(novo_usuario)
    sessao.commit()
    sessao.refresh(novo_usuario)
    return novo_usuario
