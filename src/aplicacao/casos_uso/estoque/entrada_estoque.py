from sqlalchemy.orm import Session
from src.infraestrutura.banco.modelos import ModeloEstoque, ModeloUnidade, ModeloProduto
from src.infraestrutura.auditoria.servico_auditoria import registrar_acao
from src.dominio.excecoes import UnidadeNaoEncontrada, ProdutoNaoEncontrado

def registrar_entrada(
    sessao: Session,
    unidade_id: int,
    produto_id: int,
    quantidade: int,
    usuario_id: int,
    motivo: str | None = None,
) -> ModeloEstoque:
    unidade = sessao.query(ModeloUnidade).filter(ModeloUnidade.id == unidade_id, ModeloUnidade.ativo.is_(True)).first()
    if not unidade:
        raise UnidadeNaoEncontrada(unidade_id)

    produto = sessao.query(ModeloProduto).filter(ModeloProduto.id == produto_id, ModeloProduto.ativo.is_(True)).first()
    if not produto:
        raise ProdutoNaoEncontrado(produto_id)

    estoque = sessao.query(ModeloEstoque).filter(
        ModeloEstoque.unidade_id == unidade_id,
        ModeloEstoque.produto_id == produto_id,
    ).first()

    if estoque:
        estoque.quantidade += quantidade
    else:
        estoque = ModeloEstoque(unidade_id=unidade_id, produto_id=produto_id, quantidade=quantidade)
        sessao.add(estoque)

    registrar_acao(
        sessao, "ENTRADA_ESTOQUE", "estoque",
        f"{unidade_id}-{produto_id}",
        usuario_id=usuario_id,
        detalhes={"quantidade": quantidade, "motivo": motivo, "saldo_apos": estoque.quantidade},
    )
    sessao.commit()
    sessao.refresh(estoque)
    return estoque
