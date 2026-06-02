from testes.conftest import cabecalho

def test_t13_consultar_saldo_fidelidade(cliente_http, token_cliente):
    resposta = cliente_http.get("/fidelidade/saldo", headers=cabecalho(token_cliente))
    assert resposta.status_code == 200
    dados = resposta.json()
    assert "saldo" in dados
    assert "equivalente_reais" in dados
    assert isinstance(dados["saldo"], int)

def test_t14_resgatar_sem_consentimento_lgpd(cliente_http, token_sem_lgpd):
    resposta = cliente_http.get("/fidelidade/saldo", headers=cabecalho(token_sem_lgpd))
    assert resposta.status_code == 403
    corpo = resposta.json()
    assert corpo.get("erro") == "CONSENTIMENTO_LGPD_NECESSARIO"

def test_pontos_creditados_apos_pagamento(cliente_http, ids, token_cliente):
    saldo_antes = cliente_http.get("/fidelidade/saldo", headers=cabecalho(token_cliente)).json()["saldo"]

    corpo_pedido = {
        "unidade_id": ids["unidade"],
        "canal_pedido": "APP",
        "itens": [{"produto_id": ids["produto_1"], "quantidade": 1}],
        "forma_pagamento": "MOCK",
    }
    pedido = cliente_http.post("/pedidos", json=corpo_pedido, headers=cabecalho(token_cliente))
    assert pedido.status_code == 201
    pedido_id = pedido.json()["id"]

    cliente_http.post(
        f"/pagamentos/processar/{pedido_id}",
        json={"forcar_recusa": False},
        headers=cabecalho(token_cliente),
    )

    saldo_depois = cliente_http.get("/fidelidade/saldo", headers=cabecalho(token_cliente)).json()["saldo"]
    assert saldo_depois > saldo_antes
