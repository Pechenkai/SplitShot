from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db.models.check_item import CheckItem
from app.db.models.debt import Debt
from app.db.models.game_result import GameResult
from app.db.models.game_session import GameSession
from app.db.models.participant import Participant
from app.repositories.check_item import CheckItemRepository
from app.repositories.company import CompanyRepository
from app.repositories.debt import DebtRepository
from app.repositories.game_result import GameResultRepository
from app.repositories.game_session import GameSessionRepository
from app.repositories.participant import ParticipantRepository


async def test_create_get_list_and_delete_company(db_session) -> None:
    repo = CompanyRepository(db_session)

    company = await repo.create("Friday Bar")
    fetched = await repo.get_by_id(company.id)
    companies = await repo.list_all()
    deleted = await repo.delete(company.id)
    missing = await repo.get_by_id(company.id)

    assert company.id is not None
    assert fetched is not None
    assert fetched.title == "Friday Bar"
    assert len(companies) == 1
    assert deleted is True
    assert missing is None


async def test_delete_missing_company_returns_false(db_session) -> None:
    repo = CompanyRepository(db_session)

    assert await repo.delete(9999) is False


@pytest.mark.parametrize("bad_title", ["", "   "])
async def test_create_company_rejects_blank_title(db_session, bad_title: str) -> None:
    repo = CompanyRepository(db_session)

    with pytest.raises(IntegrityError):
        await repo.create(bad_title)


async def test_delete_company_cascades_to_all_children(db_session, money) -> None:
    company_repo = CompanyRepository(db_session)
    participant_repo = ParticipantRepository(db_session)
    check_item_repo = CheckItemRepository(db_session)
    debt_repo = DebtRepository(db_session)
    game_session_repo = GameSessionRepository(db_session)
    game_result_repo = GameResultRepository(db_session)

    company = await company_repo.create("Friday Bar")
    alice = await participant_repo.create(company.id, "Alice")
    bob = await participant_repo.create(company.id, "Bob")
    await check_item_repo.create(company.id, "Pizza", money("24.90"))
    await debt_repo.create(company.id, alice.id, bob.id, money("10.00"))
    session = await game_session_repo.create(company.id, "wheel", "completed")
    await game_result_repo.create(session.id, alice.id, "winner")

    assert await company_repo.delete(company.id) is True

    for model in (Participant, CheckItem, Debt, GameSession, GameResult):
        result = await db_session.execute(select(model))
        assert result.scalars().all() == []
