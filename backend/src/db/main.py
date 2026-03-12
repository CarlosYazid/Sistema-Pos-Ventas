from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from core.settings import SETTINGS

ENGINE: AsyncEngine | None = None
AsyncSessionLocal: async_sessionmaker[AsyncSession] | None = None


def init_engine():
    """Inicializa el engine"""
    global ENGINE, AsyncSessionLocal

    ENGINE = create_async_engine(SETTINGS.db_url_async)

    AsyncSessionLocal = async_sessionmaker(bind=ENGINE, class_=AsyncSession, expire_on_commit=False)


async def init_db() -> None:
    """Inicializa el esquema (solo para dev / tests)."""
    assert ENGINE is not None

    async with ENGINE.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_engine() -> None:
    """Cierre limpio del pool."""
    if ENGINE is not None:
        await ENGINE.dispose()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    assert AsyncSessionLocal is not None

    async with AsyncSessionLocal() as session:
        yield session
