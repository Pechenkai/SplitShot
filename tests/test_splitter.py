from __future__ import annotations

from decimal import Decimal

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

    assert [(debt.debtor_id, debt.amount) for debt in debts] == [
        (1, Decimal("33.34")),
        (2, Decimal("33.33")),
    ]


def test_quick_split_rejects_duplicate_participants() -> None:
    try:
        calculate_quick_split(
            total_amount=Decimal("100.00"),
            tips_amount=Decimal("0.00"),
            participant_ids=[1, 1, 2],
            payer_id=1,
        )
    except ValueError as exc:
        assert str(exc) == "Participant ids must be unique"
    else:
        raise AssertionError("Expected duplicate participant ids to be rejected")


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

    assert [(debt.debtor_id, debt.creditor_id, debt.amount) for debt in debts] == [
        (2, 1, Decimal("990.00")),
        (3, 1, Decimal("330.00")),
    ]


def test_detailed_split_allows_empty_items_to_clear_debts() -> None:
    debts = calculate_detailed_split(
        items=[],
        tips_amount=Decimal("0.00"),
        participant_ids=[1, 2],
        payer_id=1,
    )

    assert debts == []


def test_detailed_split_rejects_duplicate_item_participants() -> None:
    try:
        calculate_detailed_split(
            items=[(Decimal("100.00"), [1, 1])],
            tips_amount=Decimal("0.00"),
            participant_ids=[1, 2],
            payer_id=1,
        )
    except ValueError as exc:
        assert str(exc) == "Item participant ids must be unique"
    else:
        raise AssertionError("Expected duplicate item participant ids to be rejected")
