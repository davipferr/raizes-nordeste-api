from typing import Any

_REF = "#/components/schemas/RespostaErro"
_TS = "2026-06-04T12:00:00+00:00"
_CAMINHO = "/rota/do/recurso"


def _resp(descricao: str, erro: str, mensagem: str, detalhes: list = []) -> dict[str, Any]:
    return {
        "description": descricao,
        "content": {
            "application/json": {
                "schema": {"$ref": _REF},
                "example": {
                    "erro": erro,
                    "mensagem": mensagem,
                    "detalhes": detalhes,
                    "timestamp": _TS,
                    "caminho": _CAMINHO,
                },
            }
        },
    }


def _resp_multiplos(descricao: str, exemplos: dict[str, tuple]) -> dict[str, Any]:
    return {
        "description": descricao,
        "content": {
            "application/json": {
                "schema": {"$ref": _REF},
                "examples": {
                    nome: {
                        "summary": e[0],
                        "value": {
                            "erro": e[0],
                            "mensagem": e[1],
                            "detalhes": e[2] if len(e) > 2 else [],
                            "timestamp": _TS,
                            "caminho": _CAMINHO,
                        },
                    }
                    for nome, e in exemplos.items()
                },
            }
        },
    }


# ─── 401 ─────────────────────────────────────────────────────────────────────
NAO_AUTENTICADO = {401: _resp(
    "Não autenticado",
    "NAO_AUTENTICADO",
    "Token de acesso ausente ou inválido.",
)}

CREDENCIAIS_INVALIDAS = {401: _resp(
    "Credenciais inválidas",
    "CREDENCIAIS_INVALIDAS",
    "E-mail ou senha inválidos.",
)}

# ─── 403 ─────────────────────────────────────────────────────────────────────
PERMISSAO_NEGADA = {403: _resp(
    "Sem permissão",
    "PERMISSAO_NEGADA",
    "Perfil 'cliente' não tem permissão para esta ação.",
)}

CONSENTIMENTO_LGPD = {403: _resp(
    "Consentimento LGPD necessário",
    "CONSENTIMENTO_LGPD_NECESSARIO",
    "Consentimento LGPD não registrado. Aceite os termos para usar o programa de fidelidade.",
)}

# ─── 404 ─────────────────────────────────────────────────────────────────────
PRODUTO_NAO_ENCONTRADO = {404: _resp(
    "Produto não encontrado",
    "PRODUTO_NAO_ENCONTRADO",
    "Produto 42 não encontrado.",
)}

UNIDADE_NAO_ENCONTRADA = {404: _resp(
    "Unidade não encontrada",
    "UNIDADE_NAO_ENCONTRADA",
    "Unidade 5 não encontrada ou inativa.",
)}

PEDIDO_NAO_ENCONTRADO = {404: _resp(
    "Pedido não encontrado",
    "PEDIDO_NAO_ENCONTRADO",
    "Pedido 10 não encontrado.",
)}

USUARIO_NAO_ENCONTRADO = {404: _resp(
    "Usuário não encontrado",
    "USUARIO_NAO_ENCONTRADO",
    "Usuário 3 não encontrado.",
)}

UNIDADE_OU_PRODUTO_NAO_ENCONTRADO = {404: _resp_multiplos(
    "Recurso não encontrado",
    {
        "UNIDADE_NAO_ENCONTRADA": ("UNIDADE_NAO_ENCONTRADA", "Unidade 5 não encontrada ou inativa."),
        "PRODUTO_NAO_ENCONTRADO": ("PRODUTO_NAO_ENCONTRADO", "Produto 42 não encontrado."),
    },
)}

RECURSOS_PEDIDO_NAO_ENCONTRADO = {404: _resp_multiplos(
    "Recurso não encontrado",
    {
        "UNIDADE_NAO_ENCONTRADA": ("UNIDADE_NAO_ENCONTRADA", "Unidade 5 não encontrada ou inativa."),
        "PRODUTO_NAO_ENCONTRADO": ("PRODUTO_NAO_ENCONTRADO", "Produto 42 não encontrado."),
        "PRODUTO_FORA_DO_CARDAPIO": (
            "PRODUTO_FORA_DO_CARDAPIO",
            "Produto 42 não está disponível no cardápio da unidade 5.",
        ),
    },
)}

# ─── 409 ─────────────────────────────────────────────────────────────────────
EMAIL_JA_CADASTRADO = {409: _resp(
    "E-mail já cadastrado",
    "EMAIL_JA_CADASTRADO",
    "Já existe um usuário com este e-mail.",
)}

ESTOQUE_INSUFICIENTE = {409: _resp(
    "Estoque insuficiente",
    "ESTOQUE_INSUFICIENTE",
    "Estoque insuficiente para o produto 7. Disponível: 3, solicitado: 10.",
    [{"campo": "itens[produto_id=7].quantidade", "problema": "Disponível: 3"}],
)}

TRANSICAO_STATUS_INVALIDA = {409: _resp(
    "Transição de status inválida",
    "TRANSICAO_STATUS_INVALIDA",
    "Transição de status inválida: AGUARDANDO_PAGAMENTO → ENTREGUE.",
)}

PEDIDO_NAO_AGUARDANDO_PAGAMENTO = {409: _resp(
    "Pedido não aguarda pagamento",
    "PEDIDO_NAO_AGUARDANDO_PAGAMENTO",
    "Pedido 10 não está aguardando pagamento (status atual: CANCELADO).",
)}

SALDO_INSUFICIENTE = {409: _resp(
    "Saldo insuficiente",
    "SALDO_INSUFICIENTE",
    "Saldo de pontos insuficiente. Disponível: 50, necessário: 100.",
)}

# ─── 422 ─────────────────────────────────────────────────────────────────────
VALIDACAO = {422: _resp(
    "Dados inválidos",
    "VALIDACAO_INVALIDA",
    "Dados da requisição inválidos.",
    [{"campo": "email", "problema": "value is not a valid email address"}],
)}

# ─── 500 ─────────────────────────────────────────────────────────────────────
ERRO_INTERNO = {500: _resp("Erro interno do servidor", "ERRO_INTERNO", "Erro interno do servidor.")}
