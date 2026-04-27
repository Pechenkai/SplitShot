from __future__ import annotations

from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.repositories.debt import DebtRepository


async def test_create_get_and_list_debts(db_session, seeded_company, seeded_participants) -> None:
    repo = DebtRepository(db_session)
    debtor, creditor, other, _ = seeded_participants

    debt = await repo.create(seeded_company.id, debtor.id, creditor.id, Decimal("8.75"))
    fetched = await repo.get_by_id(debt.id)
    by_company = await repo.list_by_company(seeded_company.id)
    by_debtor = await repo.list_by_debtor(debtor.id)
    by_creditor = await repo.list_by_creditor(creditor.id)

    assert fetched is not None
    assert fetched.amount == Decimal("8.75")
    assert [item.id for item in by_company] == [debt.id]
    assert [item.id for item in by_debtor] == [debt.id]
    assert [item.id for item in by_creditor] == [debt.id]
    assert await repo.list_by_debtor(other.id) == []


async def test_delete_debt_and_missing_behaviour(db_session, seeded_company, seeded_participants) -> None:
    repo = DebtRepository(db_session)
    debtor, creditor, *_ = seeded_participants
    debt = await repo.create(seeded_company.id, debtor.id, creditor.id, Decimal("5.00"))

    assert await repo.delete(debt.id) is True
    assert await repo.get_by_id(debt.id) is None
    assert await repo.delete(9999) is False


async def test_create_debt_rejects_same_debtor_and_creditor(db_session, seeded_company, seeded_participants) -> None:
    repo = DebtRepository(db_session)
    debtor = seeded_participants[0]

    with pytest.raises(IntegrityError):
        await repo.create(seeded_company.id, debtor.id, debtor.id, Decimal("2.00"))


async def test_create_debt_rejects_negative_amount(db_session, seeded_company, seeded_participants) -> None:
    repo = DebtRepository(db_session)
    debtor, creditor, *_ = seeded_participants

    with pytest.raises(IntegrityError):
        await repo.create(seeded_company.id, debtor.id, creditor.id, Decimal("-0.01"))


async def test_create_debt_with_zero_amount(db_session, seeded_company, seeded_participants) -> None:
    repo = DebtRepository(db_session)
    debtor, creditor, *_ = seeded_participants

    debt = await repo.create(seeded_company.id, debtor.id, creditor.id, Decimal("0.00"))

    assert debt.amount == Decimal("0.00")


async def test_multiple_debts_between_same_users(db_session, seeded_company, seeded_participants) -> None:
    repo = DebtRepository(db_session)
    debtor, creditor, *_ = seeded_participants

    debt1 = await repo.create(seeded_company.id, debtor.id, creditor.id, Decimal("10.00"))
    debt2 = await repo.create(seeded_company.id, debtor.id, creditor.id, Decimal("5.00"))

    debts = await repo.list_by_debtor(debtor.id)

    assert len(debts) == 2
    assert sum(d.amount for d in debts) == Decimal("15.00")


async def test_list_by_debtor_returns_empty_for_no_debts(db_session, seeded_company, seeded_participants) -> None:
    repo = DebtRepository(db_session)
    debtor = seeded_participants[0]

    debts = await repo.list_by_debtor(debtor.id)

    assert debts == []
