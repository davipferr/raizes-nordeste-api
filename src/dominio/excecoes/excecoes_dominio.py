class ErroNegocio(Exception):
    def __init__(self, mensagem: str, codigo: str = "ERRO_NEGOCIO"):
        self.mensagem = mensagem
        self.codigo = codigo
        super().__init__(mensagem)

class EstoqueInsuficiente(ErroNegocio):
    def __init__(self, produto_id: int, disponivel: int, solicitado: int):
        super().__init__(
            f"Estoque insuficiente para o produto {produto_id}. Disponível: {disponivel}, solicitado: {solicitado}.",
            "ESTOQUE_INSUFICIENTE",
        )
        self.produto_id = produto_id
        self.disponivel = disponivel
        self.solicitado = solicitado

class ProdutoNaoEncontrado(ErroNegocio):
    def __init__(self, produto_id: int):
        super().__init__(f"Produto {produto_id} não encontrado.", "PRODUTO_NAO_ENCONTRADO")

class UnidadeNaoEncontrada(ErroNegocio):
    def __init__(self, unidade_id: int):
        super().__init__(f"Unidade {unidade_id} não encontrada ou inativa.", "UNIDADE_NAO_ENCONTRADA")

class PedidoNaoEncontrado(ErroNegocio):
    def __init__(self, pedido_id: int):
        super().__init__(f"Pedido {pedido_id} não encontrado.", "PEDIDO_NAO_ENCONTRADO")

class TransicaoStatusInvalida(ErroNegocio):
    def __init__(self, status_atual: str, status_novo: str):
        super().__init__(
            f"Transição de status inválida: {status_atual} → {status_novo}.",
            "TRANSICAO_STATUS_INVALIDA",
        )

class PedidoNaoAguardandoPagamento(ErroNegocio):
    def __init__(self, pedido_id: int, status_atual: str):
        super().__init__(
            f"Pedido {pedido_id} não está aguardando pagamento (status atual: {status_atual}).",
            "PEDIDO_NAO_AGUARDANDO_PAGAMENTO",
        )

class ConsentimentoLgpdNaoRegistrado(ErroNegocio):
    def __init__(self):
        super().__init__(
            "Consentimento LGPD não registrado. Aceite os termos para usar o programa de fidelidade.",
            "CONSENTIMENTO_LGPD_NECESSARIO",
        )

class ProdutoForaDoCardapio(ErroNegocio):
    def __init__(self, produto_id: int, unidade_id: int):
        super().__init__(
            f"Produto {produto_id} não está disponível no cardápio da unidade {unidade_id}.",
            "PRODUTO_FORA_DO_CARDAPIO",
        )

class UsuarioNaoEncontrado(ErroNegocio):
    def __init__(self):
        super().__init__("Usuário não encontrado.", "USUARIO_NAO_ENCONTRADO")

class CredenciaisInvalidas(ErroNegocio):
    def __init__(self):
        super().__init__("E-mail ou senha inválidos.", "CREDENCIAIS_INVALIDAS")

class SaldoInsuficiente(ErroNegocio):
    def __init__(self, saldo: int, necessario: int):
        super().__init__(
            f"Saldo de pontos insuficiente. Disponível: {saldo}, necessário: {necessario}.",
            "SALDO_INSUFICIENTE",
        )
