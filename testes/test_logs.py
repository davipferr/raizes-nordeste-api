from testes.conftest import cabecalho

def test_t17_auditoria_log_pedido_criado(cliente_http, ids, token_cliente, token_admin):
    corpo = {
        "unidade_id": ids["unidade"],
        "canal_pedido": "APP",
        "itens": [{"produto_id": ids["produto_1"], "quantidade": 1}],
        "forma_pagamento": "MOCK",
    }
    pedido = cliente_http.post("/pedidos", json=corpo, headers=cabecalho(token_cliente))
    assert pedido.status_code == 201

    resposta = cliente_http.get(
        "/logs/auditoria?acao=PEDIDO_CRIADO&limite=1",
        headers=cabecalho(token_admin),
    )
    assert resposta.status_code == 200
    logs = resposta.json()
    assert isinstance(logs, list)
    assert len(logs) >= 1
    assert logs[0]["acao"] == "PEDIDO_CRIADO"
    assert logs[0]["recurso"] == "pedidos"
