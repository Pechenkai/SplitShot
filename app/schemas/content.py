from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class TongueTwisterRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str


class ForfeitCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    text: str = Field(..., min_length=1)
    kind: str = Field(default="custom", min_length=1, max_length=32)


class ForfeitRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    kind: str
    company_id: int | None
