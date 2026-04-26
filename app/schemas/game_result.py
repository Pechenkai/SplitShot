from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class GameResultCreate:
    game_session_id: int
    participant_id: int
    result_value: str


@dataclass(slots=True)
class GameResultRead:
    id: int
    game_session_id: int
    participant_id: int
    result_value: str

