from sqlalchemy.orm import Session
from src.infraestrutura.banco.modelos import ModeloPontosFidelidade, ModeloTransacaoFidelidade
from src.dominio.excecoes import ConsentimentoLgpdNaoRegistrado
from src.infraestrutura.banco.modelos import ModeloUsuario

def consultar_saldo(sessao: Session, cliente_id: int) -> dict:
    cliente = sessao.query(ModeloUsuario).filter(ModeloUsuario.id == cliente_id).first()
    if not cliente or not cliente.consentimento_lgpd:
        raise ConsentimentoLgpdNaoRegistrado()

    saldo_registro = sessao.query(ModeloPontosFidelidade).filter(
        ModeloPontosFidelidade.cliente_id == cliente_id
    ).first()
    saldo = saldo_registro.saldo if saldo_registro else 0

    return {
        "cliente_id": cliente_id,
        "saldo": saldo,
        "equivalente_reais": round(saldo / 100 * 10, 2),
    }

def consultar_historico(sessao: Session, cliente_id: int, pagina: int, limite: int) -> tuple[list, int]:
    cliente = sessao.query(ModeloUsuario).filter(ModeloUsuario.id == cliente_id).first()
    if not cliente or not cliente.consentimento_lgpd:
        raise ConsentimentoLgpdNaoRegistrado()

    consulta = sessao.query(ModeloTransacaoFidelidade).filter(
        ModeloTransacaoFidelidade.cliente_id == cliente_id
    ).order_by(ModeloTransacaoFidelidade.criado_em.desc())

    total = consulta.count()
    itens = consulta.offset((pagina - 1) * limite).limit(limite).all()
    return itens, total
