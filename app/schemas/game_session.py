from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class GameSessionCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    game_type: str = Field(..., min_length=1)


class GameSessionStatusUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    status: str = Field(..., min_length=1)


class GameSessionUpdate(GameSessionStatusUpdate):
    pass


class GameSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    game_type: str
    status: str
