import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

from app.core.config import settings
from app.models.base import Base
import app.models  # noqa: F401 — register all models on Base.metadata

# this is the Alembic Config object
config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata

# Schema for the app domain tables (empty => public). On Neon this is "vendor".
DB_SCHEMA = settings.db_schema or None


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        version_table_schema=DB_SCHEMA,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    # When targeting a non-default schema (e.g. Neon `vendor`), translate the
    # default (None) schema of every table — including unqualified DDL — to it
    # via schema_translate_map. version_table_schema places alembic_version
    # there too. The schema itself is created in its own committed transaction
    # first.
    engine_kwargs: dict = {}
    if DB_SCHEMA:
        engine_kwargs["execution_options"] = {
            "schema_translate_map": {None: DB_SCHEMA}
        }

    connectable = create_async_engine(
        settings.database_url,
        poolclass=pool.NullPool,
        **engine_kwargs,
    )

    if DB_SCHEMA:
        async with connectable.begin() as conn:
            await conn.exec_driver_sql(f'CREATE SCHEMA IF NOT EXISTS "{DB_SCHEMA}"')

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
