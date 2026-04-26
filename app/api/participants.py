from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.company import CompanyRepository
from app.repositories.participant import ParticipantRepository
from app.schemas.participant import ParticipantCreate, ParticipantRead, ParticipantUpdate

router = APIRouter(tags=["participants"])


@router.post("/companies/{company_id}/participants", response_model=ParticipantRead, status_code=status.HTTP_201_CREATED)
async def create_participant(company_id: int, payload: ParticipantCreate, db: AsyncSession = Depends(get_db)):
    if await CompanyRepository(db).get_by_id(company_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    participants = await ParticipantRepository(db).list_by_company(company_id)
    if len(participants) >= 15:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Company can have at most 15 participants")
    return await ParticipantRepository(db).create(company_id, payload.name)


@router.get("/companies/{company_id}/participants", response_model=list[ParticipantRead])
async def list_participants(company_id: int, db: AsyncSession = Depends(get_db)):
    if await CompanyRepository(db).get_by_id(company_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return await ParticipantRepository(db).list_by_company(company_id)


@router.patch("/participants/{participant_id}", response_model=ParticipantRead)
async def update_participant(participant_id: int, payload: ParticipantUpdate, db: AsyncSession = Depends(get_db)):
    participant = await ParticipantRepository(db).update_name(participant_id, payload.name)
    if participant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")
    return participant


@router.delete("/participants/{participant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_participant(participant_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await ParticipantRepository(db).delete(participant_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
