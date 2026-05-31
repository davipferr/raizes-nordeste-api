import uuid
from datetime import datetime, timezone
from decimal import Decimal

def simular_gateway(
    pedido_id: int,
    valor: Decimal,
    forma_pagamento: str,
    forcar_recusa: bool = False,
) -> tuple[bool, dict, dict]:
    transacao_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    payload_requisicao = {
        "gateway": "MockPay",
        "pedido_id": pedido_id,
        "valor": str(valor),
        "forma_pagamento": forma_pagamento,
        "timestamp": timestamp,
    }

    aprovado = not forcar_recusa

    if aprovado:
        payload_resposta = {
            "gateway": "MockPay",
            "transacao_id": transacao_id,
            "status": "APROVADO",
            "codigo_resposta": "00",
            "mensagem": "Transação aprovada com sucesso.",
            "valor_processado": str(valor),
            "forma_pagamento": forma_pagamento,
            "timestamp": timestamp,
        }
    else:
        payload_resposta = {
            "gateway": "MockPay",
            "transacao_id": transacao_id,
            "status": "RECUSADO",
            "codigo_resposta": "51",
            "mensagem": "Transação recusada pelo emissor.",
            "valor_processado": str(valor),
            "forma_pagamento": forma_pagamento,
            "timestamp": timestamp,
        }

    return aprovado, payload_requisicao, payload_resposta
