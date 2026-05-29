from sqlalchemy.orm import Session
from src.infraestrutura.banco.modelos import ModeloEstoque
from src.infraestrutura.auditoria.servico_auditoria import registrar_acao
from src.dominio.excecoes import EstoqueInsuficiente

def registrar_saida(
    sessao: Session,
    unidade_id: int,
    produto_id: int,
    quantidade: int,
    usuario_id: int,
    motivo: str | None = None,
) -> ModeloEstoque:
    estoque = sessao.query(ModeloEstoque).filter(
        ModeloEstoque.unidade_id == unidade_id,
        ModeloEstoque.produto_id == produto_id,
    ).first()

    disponivel = estoque.quantidade if estoque else 0
    if not estoque or estoque.quantidade < quantidade:
        raise EstoqueInsuficiente(produto_id, disponivel, quantidade)

    estoque.quantidade -= quantidade
    registrar_acao(
        sessao, "SAIDA_ESTOQUE", "estoque",
        f"{unidade_id}-{produto_id}",
        usuario_id=usuario_id,
        detalhes={"quantidade": quantidade, "motivo": motivo, "saldo_apos": estoque.quantidade},
    )
    sessao.commit()
    sessao.refresh(estoque)
    return estoque

def consultar_estoque_unidade(sessao: Session, unidade_id: int) -> list[dict]:
    from src.infraestrutura.banco.modelos import ModeloProduto
    resultado = (
        sessao.query(ModeloEstoque, ModeloProduto)
        .join(ModeloProduto, ModeloProduto.id == ModeloEstoque.produto_id)
        .filter(ModeloEstoque.unidade_id == unidade_id)
        .all()
    )
    return [
        {
            "produto_id": est.produto_id,
            "produto_nome": prod.nome,
            "unidade_id": est.unidade_id,
            "quantidade": est.quantidade,
            "minimo_alerta": est.minimo_alerta,
            "em_alerta": est.quantidade <= est.minimo_alerta,
            "atualizado_em": est.atualizado_em,
        }
        for est, prod in resultado
    ]
