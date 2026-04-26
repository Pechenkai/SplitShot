from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, Pool

from app.config import settings


def create_engine(
    database_url: str | None = None,
    echo: bool = False,
    poolclass: type[Pool] | None = None,
) -> AsyncEngine:
    """Create an async SQLAlchemy engine."""

    engine_kwargs: dict[str, object] = {
        "echo": echo,
    }
    if poolclass is not None:
        engine_kwargs["poolclass"] = poolclass

    return create_async_engine(database_url or settings.database_url, **engine_kwargs)


def create_session_factory(engine: AsyncEngine) -> sessionmaker:
    """Create a reusable async session factory."""

    return sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


engine = create_engine()
AsyncSessionFactory = create_session_factory(engine)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Yield an async database session."""

    async with AsyncSessionFactory() as session:
        yield session
