from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class GameResultCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    participant_id: int
    result_value: str = Field(..., min_length=1)
    result_data: dict[str, Any] | None = None


class GameResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    game_session_id: int
    participant_id: int
    result_value: str
    result_data: dict[str, Any] | None = None
