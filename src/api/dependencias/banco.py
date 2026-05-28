from sqlalchemy.orm import Session
from src.infraestrutura.banco.conexao import SessionMaker

def obter_db():
    sessao: Session = SessionMaker()
    try:
        yield sessao
    finally:
        sessao.close()
