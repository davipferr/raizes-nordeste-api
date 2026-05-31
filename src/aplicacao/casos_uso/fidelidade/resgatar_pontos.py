from sqlalchemy.orm import Session
from src.infraestrutura.banco.modelos import (
    ModeloPontosFidelidade, ModeloTransacaoFidelidade, ModeloUsuario
)
from src.infraestrutura.auditoria.servico_auditoria import registrar_acao
from src.dominio.enums import TipoTransacaoFidelidade
from src.dominio.excecoes import ConsentimentoLgpdNaoRegistrado, SaldoInsuficiente

_PONTOS_POR_RESGATE = 100
_VALOR_POR_RESGATE = 10

def resgatar_pontos(
    sessao: Session,
    cliente_id: int,
    pontos: int,
    ip_origem: str | None = None,
) -> dict:
    if pontos <= 0 or pontos % _PONTOS_POR_RESGATE != 0:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail={
            "erro": "PONTOS_INVALIDOS",
            "mensagem": f"Os pontos devem ser múltiplos de {_PONTOS_POR_RESGATE}.",
            "detalhes": [],
        })

    cliente = sessao.query(ModeloUsuario).filter(ModeloUsuario.id == cliente_id).first()
    if not cliente or not cliente.consentimento_lgpd:
        raise ConsentimentoLgpdNaoRegistrado()

    saldo_registro = sessao.query(ModeloPontosFidelidade).filter(
        ModeloPontosFidelidade.cliente_id == cliente_id
    ).with_for_update().first()

    saldo_atual = saldo_registro.saldo if saldo_registro else 0
    if saldo_atual < pontos:
        raise SaldoInsuficiente(saldo_atual, pontos)

    saldo_registro.saldo -= pontos
    desconto = (pontos // _PONTOS_POR_RESGATE) * _VALOR_POR_RESGATE

    sessao.add(ModeloTransacaoFidelidade(
        cliente_id=cliente_id,
        pontos=pontos,
        tipo=TipoTransacaoFidelidade.RESGATADO,
        descricao=f"Resgate de {pontos} pontos = R$ {desconto:.2f} de desconto",
    ))

    registrar_acao(
        sessao, "PONTOS_RESGATADOS", "fidelidade", str(cliente_id),
        usuario_id=cliente_id,
        detalhes={"pontos": pontos, "desconto_reais": desconto},
        ip_origem=ip_origem,
    )

    sessao.commit()
    sessao.refresh(saldo_registro)

    return {
        "pontos_resgatados": pontos,
        "desconto_reais": float(desconto),
        "saldo_restante": saldo_registro.saldo,
    }
