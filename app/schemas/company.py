from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CompanyCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(..., min_length=1)
    invite_code: str | None = Field(default=None, min_length=1, max_length=16)


class CompanyUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(..., min_length=1)


class CompanyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    invite_code: str
    created_at: datetime
