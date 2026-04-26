from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(slots=True)
class CheckItemCreate:
    company_id: int
    title: str
    price: Decimal


@dataclass(slots=True)
class CheckItemUpdate:
    title: str | None = None
    price: Decimal | None = None


@dataclass(slots=True)
class CheckItemRead:
    id: int
    company_id: int
    title: str
    price: Decimal

