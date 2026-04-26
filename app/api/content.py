from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.company import CompanyRepository
from app.repositories.content import ForfeitRepository, TongueTwisterRepository
from app.schemas.content import ForfeitCreate, ForfeitRead, TongueTwisterRead

router = APIRouter(tags=["content"])


@router.get("/tongue-twisters/random", response_model=TongueTwisterRead)
async def random_tongue_twister(db: AsyncSession = Depends(get_db)):
    item = await TongueTwisterRepository(db).random()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tongue twister not found")
    return item


@router.get("/forfeits/random", response_model=ForfeitRead)
async def random_forfeit(
    company_id: int | None = Query(default=None, description="Company id for custom forfeits"),
    db: AsyncSession = Depends(get_db),
):
    item = await ForfeitRepository(db).random(company_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Forfeit not found")
    return item


@router.get("/companies/{company_id}/forfeits", response_model=list[ForfeitRead])
async def list_company_forfeits(
    company_id: int,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    if await CompanyRepository(db).get_by_id(company_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return await ForfeitRepository(db).list_by_company(company_id, limit=limit, offset=offset)


@router.post("/forfeits", response_model=ForfeitRead, status_code=status.HTTP_201_CREATED)
async def create_builtin_forfeit(payload: ForfeitCreate, db: AsyncSession = Depends(get_db)):
    return await ForfeitRepository(db).create_builtin(payload.text, payload.kind)


@router.post("/companies/{company_id}/forfeits", response_model=ForfeitRead, status_code=status.HTTP_201_CREATED)
async def create_company_forfeit(company_id: int, payload: ForfeitCreate, db: AsyncSession = Depends(get_db)):
    if await CompanyRepository(db).get_by_id(company_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return await ForfeitRepository(db).create_custom(company_id, payload.text, payload.kind)
