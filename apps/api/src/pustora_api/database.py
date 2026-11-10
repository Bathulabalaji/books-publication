from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from pustora_api.config import Settings
from pustora_api.errors import ApplicationError


def create_database_engine(settings: Settings) -> AsyncEngine | None:
    if settings.database_url is None:
        return None

    return create_async_engine(
        settings.database_url.get_secret_value(),
        pool_pre_ping=True,
    )


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


async def check_database_connection(engine: AsyncEngine) -> None:
    from sqlalchemy import text

    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))


async def get_db_session(request: Request) -> AsyncIterator[AsyncSession]:
    session_factory: async_sessionmaker[AsyncSession] | None = request.app.state.db_session_factory
    if session_factory is None:
        raise ApplicationError(
            code="DATABASE_NOT_CONFIGURED",
            message="Database service is unavailable.",
            status_code=503,
        )

    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
