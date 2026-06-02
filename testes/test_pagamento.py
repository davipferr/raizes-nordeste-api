from testes.conftest import cabecalho

def _criar_pedido(cliente_http, ids, token):
    corpo = {
        "unidade_id": ids["unidade"],
        "canal_pedido": "APP",
        "itens": [{"produto_id": ids["produto_2"], "quantidade": 1}],
        "forma_pagamento": "MOCK",
    }
    resposta = cliente_http.post("/pedidos", json=corpo, headers=cabecalho(token))
    assert resposta.status_code == 201
    return resposta.json()["id"]

def test_t05_pagamento_aprovado(cliente_http, ids, token_cliente):
    pedido_id = _criar_pedido(cliente_http, ids, token_cliente)

    resposta = cliente_http.post(
        f"/pagamentos/processar/{pedido_id}",
        json={"forcar_recusa": False},
        headers=cabecalho(token_cliente),
    )
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["aprovado"] is True
    assert dados["status"] == "APROVADO"
    assert "transacao_id" in dados["payload_gateway"]
    assert dados["payload_gateway"]["codigo_resposta"] == "00"

    pedido = cliente_http.get(f"/pedidos/{pedido_id}", headers=cabecalho(token_cliente))
    assert pedido.json()["status"] == "PAGAMENTO_APROVADO"

def test_t12_pagamento_recusado(cliente_http, ids, token_cliente, token_admin):
    pedido_id = _criar_pedido(cliente_http, ids, token_cliente)

    resposta = cliente_http.post(
        f"/pagamentos/processar/{pedido_id}",
        json={"forcar_recusa": True},
        headers=cabecalho(token_cliente),
    )
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["aprovado"] is False
    assert dados["status"] == "RECUSADO"
    assert dados["payload_gateway"]["codigo_resposta"] == "51"

    pedido = cliente_http.get(f"/pedidos/{pedido_id}", headers=cabecalho(token_admin))
    assert pedido.json()["status"] == "CANCELADO"
