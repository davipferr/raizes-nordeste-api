from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pydantic_settings import BaseSettings

class Configuracoes(BaseSettings):
    database_url: str
    chave_secreta_jwt: str
    algoritmo_jwt: str = "HS256"
    minutos_expiracao_token: int = 60
    ambiente: str = "desenvolvimento"

    class Config:
        env_file = ".env"

configuracoes = Configuracoes()

motor = create_engine(
    configuracoes.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionMaker = sessionmaker(autocommit=False, autoflush=False, bind=motor)

def obter_sessao():
    sessao: Session = SessionMaker()
    try:
        yield sessao
    finally:
        sessao.close()
