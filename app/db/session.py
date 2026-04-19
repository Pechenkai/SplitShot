from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings


def create_engine(database_url: str | None = None, echo: bool = False) -> AsyncEngine:
    """Create an async SQLAlchemy engine."""

    return create_async_engine(database_url or settings.database_url, echo=echo, future=True)


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create a reusable async session factory."""

    return async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


engine = create_engine()
AsyncSessionFactory = create_session_factory(engine)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Yield an async database session."""

    async with AsyncSessionFactory() as session:
        yield session

