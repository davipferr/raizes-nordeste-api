from sqlalchemy.orm import Session
from src.infraestrutura.banco.modelos import ModeloUsuario
from src.infraestrutura.seguranca.servico_senha import verificar_senha
from src.infraestrutura.seguranca.servico_token import gerar_token_acesso
from src.infraestrutura.banco.conexao import configuracoes
from src.dominio.excecoes import CredenciaisInvalidas

def autenticar_usuario(sessao: Session, email: str, senha: str) -> dict:
    usuario = sessao.query(ModeloUsuario).filter(
        ModeloUsuario.email == email.lower().strip(),
        ModeloUsuario.ativo == True,
    ).first()

    if not usuario or not verificar_senha(senha, usuario.senha_hash):
        raise CredenciaisInvalidas()

    token = gerar_token_acesso({
        "sub": str(usuario.id),
        "email": usuario.email,
        "perfil": usuario.perfil.value,
    })

    return {
        "access_token": token,
        "token_type": "Bearer",
        "expires_in": configuracoes.minutos_expiracao_token * 60,
        "usuario": usuario,
    }
