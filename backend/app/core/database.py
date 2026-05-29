from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.core.config import settings
from app.models.base import Base

# When DB_SCHEMA is set (e.g. "vendor" on Neon), pin the asyncpg search_path so
# all unqualified table access resolves to that schema. Left empty for
# local/CI Postgres, which uses the default `public` schema.
_connect_args: dict = {}
if settings.db_schema:
    _connect_args["server_settings"] = {"search_path": f"{settings.db_schema},public"}

engine = create_async_engine(
    settings.database_url,
    echo=settings.app_env == "dev",
    pool_pre_ping=True,
    connect_args=_connect_args,
)


async def get_db() -> AsyncSession:
    async with AsyncSession(engine, expire_on_commit=False) as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
