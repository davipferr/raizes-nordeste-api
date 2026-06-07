from testes.conftest import cabecalho

def _corpo_pedido(ids: dict, canal: str = "APP", produto_id: int | None = None, quantidade: int = 1) -> dict:
    return {
        "unidade_id": ids["unidade"],
        "canal_pedido": canal,
        "itens": [{"produto_id": produto_id or ids["produto_1"], "quantidade": quantidade}],
        "forma_pagamento": "MOCK",
    }

def test_t03_listar_cardapio(cliente_http, ids, token_cliente):
    resposta = cliente_http.get(f"/cardapio/{ids['unidade']}", headers=cabecalho(token_cliente))
    assert resposta.status_code == 200
    produtos = resposta.json()
    assert isinstance(produtos, list)
    assert len(produtos) >= 1
    nomes = [p["nome"] for p in produtos]
    assert "Cuscuz com Camarão" in nomes

def test_t04_criar_pedido_valido(cliente_http, ids, token_cliente):
    resposta = cliente_http.post("/pedidos", json=_corpo_pedido(ids, canal="APP"), headers=cabecalho(token_cliente))
    assert resposta.status_code == 201
    dados = resposta.json()
    assert dados["status"] == "AGUARDANDO_PAGAMENTO"
    assert dados["canal_pedido"] == "APP"
    assert len(dados["itens"]) == 1
    assert float(dados["total"]) == 28.90
    assert "senha" not in str(dados)

def test_t06_filtrar_pedidos_por_canal(cliente_http, ids, token_cliente, token_admin):
    cliente_http.post("/pedidos", json=_corpo_pedido(ids, canal="TOTEM"), headers=cabecalho(token_cliente))
    cliente_http.post("/pedidos", json=_corpo_pedido(ids, canal="WEB"), headers=cabecalho(token_cliente))

    resposta = cliente_http.get("/pedidos?canalPedido=TOTEM", headers=cabecalho(token_admin))
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["total"] >= 1
    for item in dados["itens"]:
        assert item["canal_pedido"] == "TOTEM"

def test_t09_pedido_estoque_insuficiente(cliente_http, ids, token_cliente):
    resposta = cliente_http.post(
        "/pedidos",
        json=_corpo_pedido(ids, produto_id=ids["produto_escasso"], quantidade=5),
        headers=cabecalho(token_cliente),
    )
    assert resposta.status_code == 409
    corpo = resposta.json()
    assert corpo.get("erro") == "ESTOQUE_INSUFICIENTE"
    assert "detalhes" in corpo

def test_t10_pedido_sem_canal_pedido(cliente_http, ids, token_cliente):
    corpo = {
        "unidade_id": ids["unidade"],
        "itens": [{"produto_id": ids["produto_1"], "quantidade": 1}],
        "forma_pagamento": "MOCK",
    }
    resposta = cliente_http.post("/pedidos", json=corpo, headers=cabecalho(token_cliente))
    assert resposta.status_code == 422
    corpo_resp = resposta.json()
    assert "canal_pedido" in str(corpo_resp).lower() or "erro" in corpo_resp

def test_t15_quantidade_negativa_no_pedido(cliente_http, ids, token_cliente):
    corpo = {
        "unidade_id": ids["unidade"],
        "canal_pedido": "APP",
        "itens": [{"produto_id": ids["produto_1"], "quantidade": -1}],
        "forma_pagamento": "MOCK",
    }
    resposta = cliente_http.post("/pedidos", json=corpo, headers=cabecalho(token_cliente))
    assert resposta.status_code == 422
    corpo_resp = resposta.json()
    assert corpo_resp.get("erro") == "VALIDACAO_INVALIDA"
    assert any("quantidade" in d.get("campo", "") for d in corpo_resp.get("detalhes", []))

def test_t16_pedido_unidade_inexistente(cliente_http, ids, token_cliente):
    corpo = {
        "unidade_id": 9999,
        "canal_pedido": "APP",
        "itens": [{"produto_id": ids["produto_1"], "quantidade": 1}],
        "forma_pagamento": "MOCK",
    }
    resposta = cliente_http.post("/pedidos", json=corpo, headers=cabecalho(token_cliente))
    assert resposta.status_code == 404
    corpo_resp = resposta.json()
    assert corpo_resp.get("erro") == "UNIDADE_NAO_ENCONTRADA"
