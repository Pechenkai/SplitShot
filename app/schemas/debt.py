from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(slots=True)
class DebtCreate:
    company_id: int
    debtor_id: int
    creditor_id: int
    amount: Decimal


@dataclass(slots=True)
class DebtRead:
    id: int
    company_id: int
    debtor_id: int
    creditor_id: int
    amount: Decimal

