from decimal import Decimal
from sqlalchemy.orm import Session
from src.infraestrutura.banco.modelos import (
    ModeloUnidade, ModeloProduto, ModeloCardapioUnidade,
    ModeloEstoque, ModeloPedido, ModeloItemPedido
)
from src.infraestrutura.auditoria.servico_auditoria import registrar_acao
from src.dominio.enums import CanalPedido, StatusPedido
from src.dominio.excecoes import (
    UnidadeNaoEncontrada, ProdutoNaoEncontrado,
    ProdutoForaDoCardapio, EstoqueInsuficiente
)

def criar_pedido(
    sessao: Session,
    unidade_id: int,
    cliente_id: int,
    canal_pedido: CanalPedido,
    itens: list[dict],
    forma_pagamento: str,
    observacoes: str | None,
    ip_origem: str | None = None,
) -> ModeloPedido:
    unidade = sessao.query(ModeloUnidade).filter(
        ModeloUnidade.id == unidade_id, ModeloUnidade.ativo.is_(True)
    ).first()
    if not unidade:
        raise UnidadeNaoEncontrada(unidade_id)

    total = Decimal("0.00")
    itens_processados = []
    estoques_para_decrementar = []

    for item in itens:
        produto_id = item["produto_id"]
        quantidade = item["quantidade"]

        no_cardapio = sessao.query(ModeloCardapioUnidade).filter(
            ModeloCardapioUnidade.unidade_id == unidade_id,
            ModeloCardapioUnidade.produto_id == produto_id,
            ModeloCardapioUnidade.ativo.is_(True),
        ).first()
        if not no_cardapio:
            raise ProdutoForaDoCardapio(produto_id, unidade_id)

        produto = sessao.query(ModeloProduto).filter(
            ModeloProduto.id == produto_id, ModeloProduto.ativo.is_(True)
        ).first()
        if not produto:
            raise ProdutoNaoEncontrado(produto_id)

        estoque = sessao.query(ModeloEstoque).filter(
            ModeloEstoque.unidade_id == unidade_id,
            ModeloEstoque.produto_id == produto_id,
        ).with_for_update().first()

        disponivel = estoque.quantidade if estoque else 0
        if disponivel < quantidade:
            raise EstoqueInsuficiente(produto_id, disponivel, quantidade)

        preco_snapshot = produto.preco
        total += preco_snapshot * quantidade
        itens_processados.append({
            "produto_id": produto_id,
            "quantidade": quantidade,
            "preco_unitario": preco_snapshot,
        })
        estoques_para_decrementar.append((estoque, quantidade))

    for estoque, quantidade in estoques_para_decrementar:
        estoque.quantidade -= quantidade

    pedido = ModeloPedido(
        unidade_id=unidade_id,
        cliente_id=cliente_id,
        canal_pedido=canal_pedido,
        status=StatusPedido.AGUARDANDO_PAGAMENTO,
        total=total,
        forma_pagamento=forma_pagamento,
        observacoes=observacoes,
    )
    sessao.add(pedido)
    sessao.flush()

    for item_dados in itens_processados:
        sessao.add(ModeloItemPedido(
            pedido_id=pedido.id,
            produto_id=item_dados["produto_id"],
            quantidade=item_dados["quantidade"],
            preco_unitario=item_dados["preco_unitario"],
        ))

    registrar_acao(
        sessao, "PEDIDO_CRIADO", "pedidos", str(pedido.id),
        usuario_id=cliente_id,
        detalhes={"canal": canal_pedido.value, "total": str(total), "itens": len(itens_processados)},
        ip_origem=ip_origem,
    )

    sessao.commit()
    sessao.refresh(pedido)
    return pedido
