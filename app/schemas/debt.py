from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class DebtCreate(BaseModel):
    debtor_id: int
    creditor_id: int
    amount: Decimal = Field(..., ge=0)


class QuickSplitRequest(BaseModel):
    total_amount: Decimal = Field(..., ge=0)
    tips_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    payer_id: int


class DetailedSplitItem(BaseModel):
    title: str = Field(..., min_length=1)
    price: Decimal = Field(..., ge=0)
    participant_ids: list[int] = Field(..., min_length=1)


class DetailedSplitRequest(BaseModel):
    items: list[DetailedSplitItem] = Field(default_factory=list)
    tips_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    payer_id: int


class DebtMessageRead(BaseModel):
    message: str


class DebtRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    debtor_id: int
    creditor_id: int
    amount: Decimal
