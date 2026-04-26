from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class GameSessionCreate:
    company_id: int
    game_type: str
    status: str


@dataclass(slots=True)
class GameSessionUpdate:
    status: str


@dataclass(slots=True)
class GameSessionRead:
    id: int
    company_id: int
    game_type: str
    status: str

