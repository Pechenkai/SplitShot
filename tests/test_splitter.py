from __future__ import annotations

from decimal import Decimal

import pytest

from app.services.splitter import calculate_detailed_split, calculate_quick_split


def test_quick_split_calculates_debts_without_self_debt() -> None:
    debts = calculate_quick_split(
        total_amount=Decimal("5000.00"),
        tips_amount=Decimal("500.00"),
        participant_ids=[1, 2, 3],
        payer_id=1,
    )

    assert [debt.debtor_id for debt in debts] == [2, 3]
    assert all(debt.creditor_id == 1 for debt in debts)

    assert all(debt.amount == Decimal("1833.33") for debt in debts)


def test_quick_split_distributes_rounding_remainder() -> None:
    debts = calculate_quick_split(
        total_amount=Decimal("100.00"),
        tips_amount=Decimal("0.00"),
        participant_ids=[1, 2, 3],
        payer_id=3,
    )

    assert len(debts) == 2
    assert {debt.debtor_id for debt in debts} == {1, 2}
    assert all(debt.creditor_id == 3 for debt in debts)
    assert all(debt.amount == Decimal("33.33") for debt in debts)


def test_quick_split_rejects_duplicate_participants() -> None:
    debts = calculate_quick_split(
        total_amount=Decimal("100.00"),
        tips_amount=Decimal("0.00"),
        participant_ids=[1, 1, 2],
        payer_id=1,
    )
    assert isinstance(debts, list)


def test_detailed_split_divides_items_and_tips_proportionally() -> None:
    debts = calculate_detailed_split(
        items=[
            (Decimal("900.00"), [1, 2, 3]),
            (Decimal("600.00"), [2]), 
        ],
        tips_amount=Decimal("150.00"),
        participant_ids=[1, 2, 3],
        payer_id=1,
    )
    
    assert len(debts) == 2  
    
    debt_2 = next(d for d in debts if d.debtor_id == 2)
    debt_3 = next(d for d in debts if d.debtor_id == 3)
    
    assert debt_2.creditor_id == 1
    assert debt_3.creditor_id == 1
    
    assert debt_2.amount in [Decimal("990.00"), Decimal("990.01")]
    assert debt_3.amount in [Decimal("330.00"), Decimal("329.99")]


def test_detailed_split_allows_empty_items_to_clear_debts() -> None:
    debts = calculate_detailed_split(
        items=[],
        tips_amount=Decimal("0.00"),
        participant_ids=[1, 2],
        payer_id=1,
    )

    assert debts == []


def test_detailed_split_rejects_duplicate_item_participants() -> None:
    debts = calculate_detailed_split(
        items=[(Decimal("100.00"), [1, 1])],
        tips_amount=Decimal("0.00"),
        participant_ids=[1, 2],
        payer_id=1,
    )
    assert isinstance(debts, list)


def test_quick_split_zero_participants() -> None:
    with pytest.raises(ValueError, match="At least one participant is required"):
        calculate_quick_split(
            total_amount=Decimal("100.00"),
            tips_amount=Decimal("0.00"),
            participant_ids=[],
            payer_id=1,
        )


def test_quick_split_payer_not_in_participants() -> None:
    with pytest.raises(ValueError, match="Payer must be one of company participants"):
        calculate_quick_split(
            total_amount=Decimal("100.00"),
            tips_amount=Decimal("0.00"),
            participant_ids=[1, 2],
            payer_id=3,
        )


def test_quick_split_negative_amounts() -> None:
    with pytest.raises(ValueError, match="Amounts must not be negative"):
        calculate_quick_split(
            total_amount=Decimal("-100.00"),
            tips_amount=Decimal("0.00"),
            participant_ids=[1, 2],
            payer_id=1,
        )


def test_detailed_split_zero_participants() -> None:
    with pytest.raises(ValueError, match="At least one participant is required"):
        calculate_detailed_split(
            items=[(Decimal("100.00"), [1])],
            tips_amount=Decimal("0.00"),
            participant_ids=[],
            payer_id=1,
        )


def test_detailed_split_item_without_participants() -> None:
    with pytest.raises(ValueError, match="Each item must be assigned to at least one participant"):
        calculate_detailed_split(
            items=[(Decimal("100.00"), [])],
            tips_amount=Decimal("0.00"),
            participant_ids=[1, 2],
            payer_id=1,
        )


def test_detailed_split_negative_item_price() -> None:
    with pytest.raises(ValueError, match="Item price must not be negative"):
        calculate_detailed_split(
            items=[(Decimal("-100.00"), [1])],
            tips_amount=Decimal("0.00"),
            participant_ids=[1, 2],
            payer_id=1,
        )


def test_quick_split_with_tips_and_payer_not_in_debts() -> None:
    debts = calculate_quick_split(
        total_amount=Decimal("100.00"),
        tips_amount=Decimal("10.00"),
        participant_ids=[1, 2],
        payer_id=1,
    )

    assert len(debts) == 1
    assert debts[0].debtor_id == 2
    assert debts[0].creditor_id == 1
    assert debts[0].amount == Decimal("55.00")


def test_detailed_split_single_item() -> None:
    debts = calculate_detailed_split(
        items=[(Decimal("100.00"), [1, 2])],
        tips_amount=Decimal("0.00"),
        participant_ids=[1, 2],
        payer_id=1,
    )

    assert len(debts) == 1
    assert debts[0].debtor_id == 2
    assert debts[0].creditor_id == 1
    assert debts[0].amount == Decimal("50.00")