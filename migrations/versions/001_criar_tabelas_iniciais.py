"""criar tabelas iniciais
Revision ID: 001
Revises:
Create Date: 2026-05-26
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("nome", sa.String(150), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("senha_hash", sa.String(255), nullable=False),
        sa.Column("perfil", sa.Enum("ADMIN", "GERENTE", "COZINHA", "ATENDENTE", "CLIENTE", name="perfil_usuario"), nullable=False),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("consentimento_lgpd", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("data_consentimento", sa.DateTime(timezone=True), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_usuarios_email", "usuarios", ["email"])

    op.create_table(
        "unidades",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("nome", sa.String(150), nullable=False),
        sa.Column("endereco", sa.String(300), nullable=False),
        sa.Column("cidade", sa.String(100), nullable=False),
        sa.Column("estado", sa.String(2), nullable=False),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "produtos",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("nome", sa.String(150), nullable=False),
        sa.Column("descricao", sa.Text, nullable=True),
        sa.Column("preco", sa.Numeric(10, 2), nullable=False),
        sa.Column("categoria", sa.String(100), nullable=False),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "cardapio_unidade",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("unidade_id", sa.Integer, sa.ForeignKey("unidades.id"), nullable=False),
        sa.Column("produto_id", sa.Integer, sa.ForeignKey("produtos.id"), nullable=False),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="true"),
        sa.UniqueConstraint("unidade_id", "produto_id", name="uq_cardapio_unidade_produto"),
    )
    op.create_index("ix_cardapio_unidade_unidade_id", "cardapio_unidade", ["unidade_id"])

    op.create_table(
        "estoque",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("unidade_id", sa.Integer, sa.ForeignKey("unidades.id"), nullable=False),
        sa.Column("produto_id", sa.Integer, sa.ForeignKey("produtos.id"), nullable=False),
        sa.Column("quantidade", sa.Integer, nullable=False, server_default="0"),
        sa.Column("minimo_alerta", sa.Integer, nullable=False, server_default="5"),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("unidade_id", "produto_id", name="uq_estoque_unidade_produto"),
    )
    op.create_index("ix_estoque_unidade_id", "estoque", ["unidade_id"])

    op.create_table(
        "pedidos",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("unidade_id", sa.Integer, sa.ForeignKey("unidades.id"), nullable=False),
        sa.Column("cliente_id", sa.Integer, sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("canal_pedido", sa.Enum("APP", "TOTEM", "BALCAO", "PICKUP", "WEB", name="canal_pedido"), nullable=False),
        sa.Column("status", sa.Enum("AGUARDANDO_PAGAMENTO", "PAGAMENTO_APROVADO", "EM_PREPARO", "PRONTO", "ENTREGUE", "CANCELADO", name="status_pedido"), nullable=False),
        sa.Column("total", sa.Numeric(10, 2), nullable=False),
        sa.Column("forma_pagamento", sa.String(50), nullable=False),
        sa.Column("observacoes", sa.Text, nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_pedidos_unidade_id", "pedidos", ["unidade_id"])
    op.create_index("ix_pedidos_cliente_id", "pedidos", ["cliente_id"])

    op.create_table(
        "itens_pedido",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("pedido_id", sa.Integer, sa.ForeignKey("pedidos.id"), nullable=False),
        sa.Column("produto_id", sa.Integer, sa.ForeignKey("produtos.id"), nullable=False),
        sa.Column("quantidade", sa.Integer, nullable=False),
        sa.Column("preco_unitario", sa.Numeric(10, 2), nullable=False),
    )
    op.create_index("ix_itens_pedido_pedido_id", "itens_pedido", ["pedido_id"])

    op.create_table(
        "pagamentos",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("pedido_id", sa.Integer, sa.ForeignKey("pedidos.id"), nullable=False, unique=True),
        sa.Column("valor", sa.Numeric(10, 2), nullable=False),
        sa.Column("forma_pagamento", sa.String(50), nullable=False),
        sa.Column("status", sa.Enum("PENDENTE", "APROVADO", "RECUSADO", name="status_pagamento"), nullable=False),
        sa.Column("payload_requisicao", sa.JSON, nullable=True),
        sa.Column("payload_resposta", sa.JSON, nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "pontos_fidelidade",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("cliente_id", sa.Integer, sa.ForeignKey("usuarios.id"), nullable=False, unique=True),
        sa.Column("saldo", sa.Integer, nullable=False, server_default="0"),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "transacoes_fidelidade",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("cliente_id", sa.Integer, sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("pedido_id", sa.Integer, sa.ForeignKey("pedidos.id"), nullable=True),
        sa.Column("pontos", sa.Integer, nullable=False),
        sa.Column("tipo", sa.Enum("GANHO", "RESGATADO", name="tipo_transacao_fidelidade"), nullable=False),
        sa.Column("descricao", sa.String(255), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_transacoes_fidelidade_cliente_id", "transacoes_fidelidade", ["cliente_id"])

    op.create_table(
        "logs_auditoria",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("usuario_id", sa.Integer, sa.ForeignKey("usuarios.id"), nullable=True),
        sa.Column("acao", sa.String(100), nullable=False),
        sa.Column("recurso", sa.String(100), nullable=False),
        sa.Column("recurso_id", sa.String(50), nullable=True),
        sa.Column("detalhes", sa.JSON, nullable=True),
        sa.Column("ip_origem", sa.String(45), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_logs_auditoria_acao", "logs_auditoria", ["acao"])
    op.create_index("ix_logs_auditoria_criado_em", "logs_auditoria", ["criado_em"])

def downgrade() -> None:
    op.drop_table("logs_auditoria")
    op.drop_table("transacoes_fidelidade")
    op.drop_table("pontos_fidelidade")
    op.drop_table("pagamentos")
    op.drop_table("itens_pedido")
    op.drop_table("pedidos")
    op.drop_table("estoque")
    op.drop_table("cardapio_unidade")
    op.drop_table("produtos")
    op.drop_table("unidades")
    op.drop_table("usuarios")
    op.execute("DROP TYPE IF EXISTS tipo_transacao_fidelidade")
    op.execute("DROP TYPE IF EXISTS status_pagamento")
    op.execute("DROP TYPE IF EXISTS status_pedido")
    op.execute("DROP TYPE IF EXISTS canal_pedido")
    op.execute("DROP TYPE IF EXISTS perfil_usuario")
