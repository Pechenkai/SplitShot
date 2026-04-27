from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from decimal import Decimal

from app.db.models.check_item import CheckItem
from app.db.models.debt import Debt
from app.db.models.game_result import GameResult
from app.db.models.game_session import GameSession
from app.db.models.participant import Participant
from app.repositories.company import CompanyRepository
from app.repositories.debt import DebtRepository
from app.repositories.game_result import GameResultRepository
from app.repositories.game_session import GameSessionRepository
from app.repositories.participant import ParticipantRepository


async def test_complete_workflow(db_session) -> None:
    company_repo = CompanyRepository(db_session)
    participant_repo = ParticipantRepository(db_session)
    session_repo = GameSessionRepository(db_session)
    result_repo = GameResultRepository(db_session)
    debt_repo = DebtRepository(db_session)

    company = await company_repo.create("Test Bar")

    alice = await participant_repo.create(company.id, "Alice")
    bob = await participant_repo.create(company.id, "Bob")
    charlie = await participant_repo.create(company.id, "Charlie")

    game = await session_repo.create(company.id, "wheel", "completed")
    await result_repo.create(game.id, alice.id, "winner")
    await result_repo.create(game.id, bob.id, "loser")

    await debt_repo.create(company.id, alice.id, bob.id, Decimal("10.00"))
    await debt_repo.create(company.id, charlie.id, bob.id, Decimal("5.00"))

    participants = await participant_repo.list_by_company(company.id)
    assert len(participants) == 3

    results = await result_repo.list_by_game_session(game.id)
    assert len(results) == 2

    debts = await debt_repo.list_by_company(company.id)
    assert len(debts) == 2
    total_debt = sum(d.amount for d in debts)
    assert total_debt == Decimal("15.00")

    await session_repo.update_status(game.id, "archived")
    await company_repo.delete(company.id)

    for model in (Participant, GameSession, GameResult, Debt, CheckItem):
        result = await db_session.execute(select(model))
        assert result.scalars().all() == []


async def test_cross_company_isolation(db_session) -> None:
    company_repo = CompanyRepository(db_session)
    participant_repo = ParticipantRepository(db_session)

    company1 = await company_repo.create("Bar 1")
    company2 = await company_repo.create("Bar 2")

    await participant_repo.create(company1.id, "Alice")
    await participant_repo.create(company2.id, "Bob")

    participants1 = await participant_repo.list_by_company(company1.id)
    participants2 = await participant_repo.list_by_company(company2.id)

    assert len(participants1) == 1
    assert participants1[0].name == "Alice"
    assert len(participants2) == 1
    assert participants2[0].name == "Bob"


async def test_orphan_prevention(db_session, seeded_company, seeded_participants) -> None:
    debt_repo = DebtRepository(db_session)

    with pytest.raises(IntegrityError):
        await debt_repo.create(seeded_company.id, 99999, 99998, Decimal("10.00"))
