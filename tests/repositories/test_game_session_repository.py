from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db.models.game_result import GameResult
from app.repositories.game_result import GameResultRepository
from app.repositories.game_session import GameSessionRepository


async def test_create_get_list_update_and_delete_game_session(db_session, seeded_company) -> None:
    repo = GameSessionRepository(db_session)

    game_session = await repo.create(seeded_company.id, "wheel", "planned")
    fetched = await repo.get_by_id(game_session.id)
    sessions = await repo.list_by_company(seeded_company.id)
    updated = await repo.update_status(game_session.id, "completed")
    deleted = await repo.delete(game_session.id)

    assert fetched is not None
    assert fetched.game_type == "wheel"
    assert len(sessions) == 1
    assert updated is not None
    assert updated.status == "completed"
    assert deleted is True
    assert await repo.get_by_id(game_session.id) is None


async def test_update_missing_game_session_returns_none(db_session) -> None:
    repo = GameSessionRepository(db_session)

    assert await repo.update_status(9999, "completed") is None


async def test_delete_missing_game_session_returns_false(db_session) -> None:
    repo = GameSessionRepository(db_session)

    assert await repo.delete(9999) is False


@pytest.mark.parametrize("bad_game_type", ["", "   "])
async def test_create_game_session_rejects_blank_game_type(
    db_session,
    seeded_company,
    bad_game_type: str,
) -> None:
    repo = GameSessionRepository(db_session)

    with pytest.raises(IntegrityError):
        await repo.create(seeded_company.id, bad_game_type, "planned")


@pytest.mark.parametrize("bad_status", ["", "   "])
async def test_create_game_session_rejects_blank_status(
    db_session,
    seeded_company,
    bad_status: str,
) -> None:
    repo = GameSessionRepository(db_session)

    with pytest.raises(IntegrityError):
        await repo.create(seeded_company.id, "wheel", bad_status)


async def test_delete_game_session_cascades_to_results(db_session, seeded_company, seeded_participants) -> None:
    session_repo = GameSessionRepository(db_session)
    result_repo = GameResultRepository(db_session)

    game_session = await session_repo.create(seeded_company.id, "tongue_twister", "completed")
    await result_repo.create(game_session.id, seeded_participants[0].id, "winner")

    assert await session_repo.delete(game_session.id) is True

    result = await db_session.execute(select(GameResult))
    assert result.scalars().all() == []
