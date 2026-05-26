from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infraestrutura.banco.conexao import configuracoes
from src.infraestrutura.banco.modelos.modelo_base import ModeloBase
import src.infraestrutura.banco.modelos

config = context.config
config.set_main_option("sqlalchemy.url", configuracoes.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

alvo_metadados = ModeloBase.metadata

def executar_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=alvo_metadados,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def executar_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=alvo_metadados)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    executar_migrations_offline()
else:
    executar_migrations_online()
