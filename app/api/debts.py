from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.company import CompanyRepository
from app.repositories.debt import DebtRepository
from app.repositories.participant import ParticipantRepository
from app.schemas.debt import DebtMessageRead, DebtRead, DetailedSplitRequest, QuickSplitRequest
from app.services.splitter import calculate_detailed_split, calculate_quick_split, format_debt_message, save_company_debts

router = APIRouter(tags=["debts"])


@router.get("/companies/{company_id}/debts", response_model=list[DebtRead])
async def list_debts(company_id: int, db: AsyncSession = Depends(get_db)):
    if await CompanyRepository(db).get_by_id(company_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return await DebtRepository(db).list_by_company(company_id)


@router.get("/companies/{company_id}/debts/message", response_model=DebtMessageRead)
async def get_debt_message(company_id: int, db: AsyncSession = Depends(get_db)):
    if await CompanyRepository(db).get_by_id(company_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    participants = await ParticipantRepository(db).list_by_company(company_id)
    debts = await DebtRepository(db).list_by_company(company_id)
    return {"message": format_debt_message(debts, {participant.id: participant.name for participant in participants})}


@router.post("/companies/{company_id}/split/quick", response_model=list[DebtRead])
async def quick_split(company_id: int, payload: QuickSplitRequest, db: AsyncSession = Depends(get_db)):
    if await CompanyRepository(db).get_by_id(company_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    participants = await ParticipantRepository(db).list_by_company(company_id)
    if not participants:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Company has no participants")

    participant_ids = [participant.id for participant in participants]
    if payload.payer_id not in participant_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payer must belong to company")

    calculated = calculate_quick_split(
        total_amount=payload.total_amount,
        tips_amount=payload.tips_amount,
        participant_ids=participant_ids,
        payer_id=payload.payer_id,
    )
    return await save_company_debts(DebtRepository(db), company_id, calculated)


@router.post("/companies/{company_id}/split/detailed", response_model=list[DebtRead])
async def detailed_split(company_id: int, payload: DetailedSplitRequest, db: AsyncSession = Depends(get_db)):
    if await CompanyRepository(db).get_by_id(company_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    participants = await ParticipantRepository(db).list_by_company(company_id)
    if not participants:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Company has no participants")

    participant_ids = [participant.id for participant in participants]
    if payload.payer_id not in participant_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payer must belong to company")

    try:
        calculated = calculate_detailed_split(
            items=[(item.price, item.participant_ids) for item in payload.items],
            tips_amount=payload.tips_amount,
            participant_ids=participant_ids,
            payer_id=payload.payer_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return await save_company_debts(DebtRepository(db), company_id, calculated)
