from passlib.context import CryptContext

_contexto = CryptContext(schemes=["bcrypt"], deprecated="auto")

def gerar_hash(senha: str) -> str:
    return _contexto.hash(senha)

def verificar_senha(senha_plain: str, senha_hash: str) -> bool:
    return _contexto.verify(senha_plain, senha_hash)
