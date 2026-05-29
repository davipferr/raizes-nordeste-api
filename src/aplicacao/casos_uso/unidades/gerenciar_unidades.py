from sqlalchemy.orm import Session
from src.infraestrutura.banco.modelos import ModeloUnidade
from src.dominio.excecoes import UnidadeNaoEncontrada

def listar_unidades(sessao: Session, pagina: int, limite: int, apenas_ativas: bool = True):
    consulta = sessao.query(ModeloUnidade)
    if apenas_ativas:
        consulta = consulta.filter(ModeloUnidade.ativo.is_(True))
    total = consulta.count()
    itens = consulta.offset((pagina - 1) * limite).limit(limite).all()
    return itens, total

def obter_unidade(sessao: Session, unidade_id: int) -> ModeloUnidade:
    unidade = sessao.query(ModeloUnidade).filter(ModeloUnidade.id == unidade_id).first()
    if not unidade:
        raise UnidadeNaoEncontrada(unidade_id)
    return unidade

def criar_unidade(sessao: Session, nome: str, endereco: str, cidade: str, estado: str) -> ModeloUnidade:
    unidade = ModeloUnidade(nome=nome, endereco=endereco, cidade=cidade, estado=estado, ativo=True)
    sessao.add(unidade)
    sessao.commit()
    sessao.refresh(unidade)
    return unidade

def atualizar_unidade(sessao: Session, unidade_id: int, dados: dict) -> ModeloUnidade:
    unidade = obter_unidade(sessao, unidade_id)
    for campo, valor in dados.items():
        if valor is not None:
            setattr(unidade, campo, valor)
    sessao.commit()
    sessao.refresh(unidade)
    return unidade
