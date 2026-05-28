from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from src.infraestrutura.banco.conexao import configuracoes

def gerar_token_acesso(dados: dict) -> str:
    payload = dados.copy()
    expiracao = datetime.now(timezone.utc) + timedelta(minutes=configuracoes.minutos_expiracao_token)
    payload.update({"exp": expiracao})
    return jwt.encode(payload, configuracoes.chave_secreta_jwt, algorithm=configuracoes.algoritmo_jwt)

def decodificar_token(token: str) -> dict:
    try:
        return jwt.decode(token, configuracoes.chave_secreta_jwt, algorithms=[configuracoes.algoritmo_jwt])
    except JWTError:
        return {}
