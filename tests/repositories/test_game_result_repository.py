from __future__ import annotations

import pytest
from sqlalchemy.exc import IntegrityError

from app.repositories.game_result import GameResultRepository
from app.repositories.game_session import GameSessionRepository


async def test_create_get_list_and_delete_game_result(db_session, seeded_company, seeded_participants) -> None:
    session_repo = GameSessionRepository(db_session)
    result_repo = GameResultRepository(db_session)
    game_session = await session_repo.create(seeded_company.id, "wheel", "completed")

    result = await result_repo.create(game_session.id, seeded_participants[0].id, "winner")
    fetched = await result_repo.get_by_id(result.id)
    by_session = await result_repo.list_by_game_session(game_session.id)
    by_participant = await result_repo.list_by_participant(seeded_participants[0].id)
    deleted = await result_repo.delete(result.id)

    assert fetched is not None
    assert fetched.result_value == "winner"
    assert [item.id for item in by_session] == [result.id]
    assert [item.id for item in by_participant] == [result.id]
    assert deleted is True
    assert await result_repo.get_by_id(result.id) is None


async def test_delete_missing_game_result_returns_false(db_session) -> None:
    repo = GameResultRepository(db_session)

    assert await repo.delete(9999) is False


@pytest.mark.parametrize("bad_value", ["", "   "])
async def test_create_game_result_rejects_blank_result_value(
    db_session,
    seeded_company,
    seeded_participants,
    bad_value: str,
) -> None:
    session_repo = GameSessionRepository(db_session)
    result_repo = GameResultRepository(db_session)
    game_session = await session_repo.create(seeded_company.id, "wheel", "completed")

    with pytest.raises(IntegrityError):
        await result_repo.create(game_session.id, seeded_participants[0].id, bad_value)


async def test_multiple_results_for_same_game_session(db_session, seeded_company, seeded_participants) -> None:
    session_repo = GameSessionRepository(db_session)
    result_repo = GameResultRepository(db_session)
    game_session = await session_repo.create(seeded_company.id, "wheel", "completed")
    p1, p2, p3, _ = seeded_participants

    r1 = await result_repo.create(game_session.id, p1.id, "winner")
    r2 = await result_repo.create(game_session.id, p2.id, "loser")
    r3 = await result_repo.create(game_session.id, p3.id, "2nd_place")

    results = await result_repo.list_by_game_session(game_session.id)

    assert len(results) == 3
    assert {r.result_value for r in results} == {"winner", "loser", "2nd_place"}


async def test_one_participant_multiple_results(db_session, seeded_company, seeded_participants) -> None:
    session_repo = GameSessionRepository(db_session)
    result_repo = GameResultRepository(db_session)
    participant = seeded_participants[0]

    session1 = await session_repo.create(seeded_company.id, "wheel", "completed")
    session2 = await session_repo.create(seeded_company.id, "sobriety_test", "completed")

    r1 = await result_repo.create(session1.id, participant.id, "winner")
    r2 = await result_repo.create(session2.id, participant.id, "0.05")

    results = await result_repo.list_by_participant(participant.id)

    assert len(results) == 2
