from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from decimal import Decimal

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.config import settings
from app.db.base import Base
from app.db.models import check_item, company, debt, game_result, game_session, participant  # noqa: F401
from app.db.session import create_engine, create_session_factory
from app.repositories.company import CompanyRepository
from app.repositories.participant import ParticipantRepository


def run_migrations(database_url: str, revision: str) -> None:
    """Run Alembic migrations against the provided database URL."""

    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", database_url)
    if revision == "head":
        command.upgrade(config, revision)
    else:
        command.downgrade(config, revision)


async def truncate_all_tables(engine: AsyncEngine) -> None:
    table_names = [table.name for table in reversed(Base.metadata.sorted_tables)]
    if not table_names:
        return

    joined_names = ", ".join(table_names)
    async with engine.begin() as conn:
        await conn.execute(text(f"TRUNCATE {joined_names} RESTART IDENTITY CASCADE"))


@pytest_asyncio.fixture(scope="session")
async def async_engine() -> AsyncIterator[AsyncEngine]:
    await asyncio.to_thread(run_migrations, settings.test_database_url, "base")
    await asyncio.to_thread(run_migrations, settings.test_database_url, "head")

    engine = create_engine(settings.test_database_url, poolclass=NullPool)

    yield engine

    await engine.dispose()
    await asyncio.to_thread(run_migrations, settings.test_database_url, "base")


@pytest_asyncio.fixture(scope="session")
async def async_session_factory(
    async_engine: AsyncEngine,
) -> sessionmaker:
    return create_session_factory(async_engine)


@pytest_asyncio.fixture
async def db_session(
    async_engine: AsyncEngine,
    async_session_factory: sessionmaker,
) -> AsyncIterator[AsyncSession]:
    await truncate_all_tables(async_engine)
    async with async_session_factory() as session:
        yield session
    await truncate_all_tables(async_engine)


@pytest_asyncio.fixture
async def seeded_company(db_session: AsyncSession):
    repo = CompanyRepository(db_session)
    return await repo.create("Friday Bar")


@pytest_asyncio.fixture
async def seeded_participants(db_session: AsyncSession, seeded_company):
    repo = ParticipantRepository(db_session)
    participants = [
        await repo.create(seeded_company.id, "Alice"),
        await repo.create(seeded_company.id, "Bob"),
        await repo.create(seeded_company.id, "Charlie"),
        await repo.create(seeded_company.id, "Diana"),
    ]
    return participants


@pytest.fixture
def money() -> type[Decimal]:
    return Decimal
