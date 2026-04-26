from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable, Mapping

from app.db.models.debt import Debt
from app.repositories.debt import DebtRepository

MONEY_QUANT = Decimal("0.01")


@dataclass(frozen=True, slots=True)
class CalculatedDebt:
    debtor_id: int
    creditor_id: int
    amount: Decimal


def _to_money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def _validate_unique_ids(ids: list[int], message: str) -> None:
    if len(ids) != len(set(ids)):
        raise ValueError(message)


def _split_money_evenly(total: Decimal, ids: list[int]) -> dict[int, Decimal]:
    rounded_total = _to_money(total)
    total_cents = int(rounded_total / MONEY_QUANT)
    base_cents = total_cents // len(ids)
    remainder_cents = total_cents % len(ids)

    shares = {participant_id: MONEY_QUANT * base_cents for participant_id in ids}
    for participant_id in ids[:remainder_cents]:
        shares[participant_id] += MONEY_QUANT

    return shares


def calculate_quick_split(
    total_amount: Decimal,
    tips_amount: Decimal,
    participant_ids: Iterable[int],
    payer_id: int,
) -> list[CalculatedDebt]:
    ids = list(participant_ids)
    if not ids:
        raise ValueError("At least one participant is required")
    _validate_unique_ids(ids, "Participant ids must be unique")
    if payer_id not in ids:
        raise ValueError("Payer must be one of company participants")
    if total_amount < 0 or tips_amount < 0:
        raise ValueError("Amounts must not be negative")

    shares = _split_money_evenly(total_amount + tips_amount, ids)

    return [
        CalculatedDebt(debtor_id=participant_id, creditor_id=payer_id, amount=amount)
        for participant_id, amount in shares.items()
        if participant_id != payer_id and amount > 0
    ]


def _quantize_shares(shares: dict[int, Decimal]) -> dict[int, Decimal]:
    rounded = {participant_id: _to_money(amount) for participant_id, amount in shares.items()}
    target_total = _to_money(sum(shares.values(), Decimal("0.00")))
    current_total = sum(rounded.values(), Decimal("0.00"))
    cents_delta = int((target_total - current_total) / MONEY_QUANT)

    if cents_delta == 0:
        return rounded

    sign = 1 if cents_delta > 0 else -1
    sorted_ids = sorted(shares, key=lambda participant_id: shares[participant_id], reverse=sign > 0)
    for participant_id in sorted_ids[: abs(cents_delta)]:
        rounded[participant_id] += MONEY_QUANT * sign

    return rounded


def _build_debts_from_shares(shares: dict[int, Decimal], payer_id: int) -> list[CalculatedDebt]:
    rounded_shares = _quantize_shares(shares)
    return [
        CalculatedDebt(debtor_id=participant_id, creditor_id=payer_id, amount=amount)
        for participant_id, amount in rounded_shares.items()
        if participant_id != payer_id and amount > 0
    ]


def calculate_detailed_split(
    items: Iterable[tuple[Decimal, Iterable[int]]],
    tips_amount: Decimal,
    participant_ids: Iterable[int],
    payer_id: int,
) -> list[CalculatedDebt]:
    ids = list(participant_ids)
    if not ids:
        raise ValueError("At least one participant is required")
    _validate_unique_ids(ids, "Participant ids must be unique")
    if payer_id not in ids:
        raise ValueError("Payer must be one of company participants")
    if tips_amount < 0:
        raise ValueError("Tips amount must not be negative")

    shares: dict[int, Decimal] = {participant_id: Decimal("0.00") for participant_id in ids}
    total_without_tips = Decimal("0.00")
    known_ids = set(ids)

    for price, item_participant_ids in items:
        assigned_ids = list(item_participant_ids)
        if price < 0:
            raise ValueError("Item price must not be negative")
        if not assigned_ids:
            raise ValueError("Each item must be assigned to at least one participant")
        _validate_unique_ids(assigned_ids, "Item participant ids must be unique")
        if not set(assigned_ids).issubset(known_ids):
            raise ValueError("Item participant must belong to company")

        item_share = price / Decimal(len(assigned_ids))
        for participant_id in assigned_ids:
            shares[participant_id] += item_share
        total_without_tips += price

    if tips_amount and total_without_tips > 0:
        for participant_id, amount in shares.items():
            shares[participant_id] = amount + tips_amount * (amount / total_without_tips)

    return _build_debts_from_shares(shares, payer_id)


def format_debt_message(debts: Iterable[Debt], participant_names: Mapping[int, str] | None = None) -> str:
    names = participant_names or {}
    lines = ["SplitShot: долги по счету"]
    has_debts = False
    for debt in debts:
        has_debts = True
        debtor = names.get(debt.debtor_id, f"Участник #{debt.debtor_id}")
        creditor = names.get(debt.creditor_id, f"Участник #{debt.creditor_id}")
        lines.append(f"{debtor} -> {creditor}: {debt.amount} ₽")
    if not has_debts:
        lines.append("Долгов нет")
    return "\n".join(lines)


async def save_company_debts(
    repository: DebtRepository,
    company_id: int,
    debts: Iterable[CalculatedDebt],
) -> list[Debt]:
    await repository.delete_by_company(company_id)
    saved: list[Debt] = []
    for debt in debts:
        saved.append(
            await repository.create(
                company_id=company_id,
                debtor_id=debt.debtor_id,
                creditor_id=debt.creditor_id,
                amount=debt.amount,
            )
        )
    return saved
