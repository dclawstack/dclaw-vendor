from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.core.config import settings
from app.models.base import Base

# When DB_SCHEMA is set (e.g. "vendor" on Neon), translate the default (None)
# schema of every model/table to that schema for all ORM + DDL operations.
# Left empty for local/CI Postgres, which uses the default `public` schema.
# (asyncpg's `server_settings` search_path is unreliable through this dialect,
# so schema_translate_map is used instead.)
_engine_kwargs: dict = {}
if settings.db_schema:
    _engine_kwargs["execution_options"] = {
        "schema_translate_map": {None: settings.db_schema}
    }

engine = create_async_engine(
    settings.database_url,
    echo=settings.app_env == "dev",
    pool_pre_ping=True,
    **_engine_kwargs,
)


async def get_db() -> AsyncSession:
    async with AsyncSession(engine, expire_on_commit=False) as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    async with engine.begin() as conn:
        if settings.db_schema:
            await conn.exec_driver_sql(
                f'CREATE SCHEMA IF NOT EXISTS "{settings.db_schema}"'
            )
        await conn.run_sync(Base.metadata.create_all)
