from __future__ import annotations

from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.repositories.check_item import CheckItemRepository


async def test_create_get_list_update_and_delete_check_item(db_session, seeded_company) -> None:
    repo = CheckItemRepository(db_session)

    item = await repo.create(seeded_company.id, "Pizza", Decimal("19.90"))
    fetched = await repo.get_by_id(item.id)
    items = await repo.list_by_company(seeded_company.id)

    assert fetched is not None
    assert fetched.title == "Pizza"
    assert fetched.price == Decimal("19.90")
    assert len(items) == 1

    updated = await repo.update(item.id, title="Large Pizza", price=Decimal("24.50"))

    assert updated is not None
    assert updated.title == "Large Pizza"
    assert updated.price == Decimal("24.50")

    deleted = await repo.delete(item.id)
    assert deleted is True
    assert await repo.get_by_id(item.id) is None


async def test_update_missing_check_item_returns_none(db_session) -> None:
    repo = CheckItemRepository(db_session)

    assert await repo.update(9999, title="Ghost") is None


async def test_delete_missing_check_item_returns_false(db_session) -> None:
    repo = CheckItemRepository(db_session)

    assert await repo.delete(9999) is False


async def test_create_check_item_rejects_negative_price(db_session, seeded_company) -> None:
    repo = CheckItemRepository(db_session)

    with pytest.raises(IntegrityError):
        await repo.create(seeded_company.id, "Beer", Decimal("-1.00"))


@pytest.mark.parametrize("bad_title", ["", "   "])
async def test_create_check_item_rejects_blank_title(db_session, seeded_company, bad_title: str) -> None:
    repo = CheckItemRepository(db_session)

    with pytest.raises(IntegrityError):
        await repo.create(seeded_company.id, bad_title, Decimal("2.00"))
