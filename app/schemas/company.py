from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class CompanyCreate:
    title: str


@dataclass(slots=True)
class CompanyRead:
    id: int
    title: str
    created_at: datetime

