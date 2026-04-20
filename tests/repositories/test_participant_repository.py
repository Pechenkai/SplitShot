from __future__ import annotations

import pytest
from sqlalchemy.exc import IntegrityError

from app.repositories.participant import ParticipantRepository


async def test_create_get_list_update_and_delete_participant(db_session, seeded_company) -> None:
    repo = ParticipantRepository(db_session)

    participant = await repo.create(seeded_company.id, "Alice")
    fetched = await repo.get_by_id(participant.id)
    items = await repo.list_by_company(seeded_company.id)

    assert participant.id is not None
    assert fetched is not None
    assert fetched.name == "Alice"
    assert [item.name for item in items] == ["Alice"]

    updated = await repo.update_name(participant.id, "Alicia")

    assert updated is not None
    assert updated.name == "Alicia"

    deleted = await repo.delete(participant.id)
    assert deleted is True
    assert await repo.get_by_id(participant.id) is None


async def test_update_missing_participant_returns_none(db_session) -> None:
    repo = ParticipantRepository(db_session)

    assert await repo.update_name(9999, "Ghost") is None


async def test_delete_missing_participant_returns_false(db_session) -> None:
    repo = ParticipantRepository(db_session)

    assert await repo.delete(9999) is False


@pytest.mark.parametrize("bad_name", ["", "   "])
async def test_create_participant_rejects_blank_name(db_session, seeded_company, bad_name: str) -> None:
    repo = ParticipantRepository(db_session)

    with pytest.raises(IntegrityError):
        await repo.create(seeded_company.id, bad_name)
