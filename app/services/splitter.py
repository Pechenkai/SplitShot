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


def calculate_quick_split(
    total_amount: Decimal,
    tips_amount: Decimal,
    participant_ids: Iterable[int],
    payer_id: int,
) -> list[CalculatedDebt]:
    ids = list(participant_ids)
    if not ids:
        raise ValueError("At least one participant is required")
    if payer_id not in ids:
        raise ValueError("Payer must be one of company participants")
    if total_amount < 0 or tips_amount < 0:
        raise ValueError("Amounts must not be negative")

    total = total_amount + tips_amount
    share = _to_money(total / Decimal(len(ids)))

    return [
        CalculatedDebt(debtor_id=participant_id, creditor_id=payer_id, amount=share) for participant_id in ids if participant_id != payer_id
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
    if payer_id not in ids:
        raise ValueError("Payer must be one of company participants")
    if tips_amount < 0:
        raise ValueError("Tips amount must not be negative")

    shares: dict[int, Decimal] = {participant_id: Decimal("0.00") for participant_id in ids}
    total_without_tips = Decimal("0.00")
    known_ids = set(ids)

    for price, item_participant_ids in items:
        assigned_ids = list(dict.fromkeys(item_participant_ids))
        if price < 0:
            raise ValueError("Item price must not be negative")
        if not assigned_ids:
            raise ValueError("Each item must be assigned to at least one participant")
        if not set(assigned_ids).issubset(known_ids):
            raise ValueError("Item participant must belong to company")

        item_share = price / Decimal(len(assigned_ids))
        for participant_id in assigned_ids:
            shares[participant_id] += item_share
        total_without_tips += price

    if tips_amount and total_without_tips > 0:
        for participant_id, amount in shares.items():
            shares[participant_id] = amount + tips_amount * (amount / total_without_tips)

    return [
        CalculatedDebt(debtor_id=participant_id, creditor_id=payer_id, amount=_to_money(amount))
        for participant_id, amount in shares.items()
        if participant_id != payer_id and _to_money(amount) > 0
    ]


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
