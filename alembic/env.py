# alembic/env.py

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Adicione o diretório do projeto ao sys.path para permitir importações
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Carrega o objeto Config do Alembic
config = context.config

# Configuração de logging
fileConfig(config.config_file_name)

from app.models.base import Base
from app.models.role import Role
from app.models.user import User
from app.models.customer import Customer
from app.models.offer import Offer
from app.models.offer_document import OfferDocument
from app.models.calculations import InssSynthesizedCalculation

target_metadata = Base.metadata


def run_migrations_offline():
    """Executa migrações em modo offline."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Executa migrações em modo online."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
