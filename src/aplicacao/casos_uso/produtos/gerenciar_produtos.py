from decimal import Decimal
from sqlalchemy.orm import Session
from src.infraestrutura.banco.modelos import ModeloProduto, ModeloCardapioUnidade
from src.dominio.excecoes import ProdutoNaoEncontrado, UnidadeNaoEncontrada

def listar_produtos(sessao: Session, pagina: int, limite: int, categoria: str | None = None, apenas_ativos: bool = True):
    consulta = sessao.query(ModeloProduto)
    if apenas_ativos:
        consulta = consulta.filter(ModeloProduto.ativo.is_(True))
    if categoria:
        consulta = consulta.filter(ModeloProduto.categoria.ilike(f"%{categoria}%"))
    total = consulta.count()
    itens = consulta.offset((pagina - 1) * limite).limit(limite).all()
    return itens, total

def obter_produto(sessao: Session, produto_id: int) -> ModeloProduto:
    produto = sessao.query(ModeloProduto).filter(ModeloProduto.id == produto_id).first()
    if not produto:
        raise ProdutoNaoEncontrado(produto_id)
    return produto

def criar_produto(sessao: Session, nome: str, descricao: str | None, preco: Decimal, categoria: str) -> ModeloProduto:
    produto = ModeloProduto(nome=nome, descricao=descricao, preco=preco, categoria=categoria, ativo=True)
    sessao.add(produto)
    sessao.commit()
    sessao.refresh(produto)
    return produto

def atualizar_produto(sessao: Session, produto_id: int, dados: dict) -> ModeloProduto:
    produto = obter_produto(sessao, produto_id)
    for campo, valor in dados.items():
        if valor is not None:
            setattr(produto, campo, valor)
    sessao.commit()
    sessao.refresh(produto)
    return produto

def listar_cardapio_unidade(sessao: Session, unidade_id: int) -> list[ModeloProduto]:
    from src.infraestrutura.banco.modelos import ModeloUnidade
    unidade = sessao.query(ModeloUnidade).filter(ModeloUnidade.id == unidade_id, ModeloUnidade.ativo.is_(True)).first()
    if not unidade:
        raise UnidadeNaoEncontrada(unidade_id)

    resultado = (
        sessao.query(ModeloProduto)
        .join(ModeloCardapioUnidade, ModeloCardapioUnidade.produto_id == ModeloProduto.id)
        .filter(
            ModeloCardapioUnidade.unidade_id == unidade_id,
            ModeloCardapioUnidade.ativo.is_(True),
            ModeloProduto.ativo.is_(True),
        )
        .all()
    )
    return resultado

def adicionar_produto_cardapio(sessao: Session, unidade_id: int, produto_id: int) -> None:
    from src.infraestrutura.banco.modelos import ModeloUnidade
    unidade = sessao.query(ModeloUnidade).filter(ModeloUnidade.id == unidade_id).first()
    if not unidade:
        raise UnidadeNaoEncontrada(unidade_id)
    produto = obter_produto(sessao, produto_id)

    existente = sessao.query(ModeloCardapioUnidade).filter(
        ModeloCardapioUnidade.unidade_id == unidade_id,
        ModeloCardapioUnidade.produto_id == produto_id,
    ).first()

    if existente:
        existente.ativo = True
    else:
        sessao.add(ModeloCardapioUnidade(unidade_id=unidade_id, produto_id=produto_id, ativo=True))
    sessao.commit()

def remover_produto_cardapio(sessao: Session, unidade_id: int, produto_id: int) -> None:
    item = sessao.query(ModeloCardapioUnidade).filter(
        ModeloCardapioUnidade.unidade_id == unidade_id,
        ModeloCardapioUnidade.produto_id == produto_id,
    ).first()
    if item:
        item.ativo = False
        sessao.commit()
