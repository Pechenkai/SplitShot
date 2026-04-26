from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.company import CompanyRepository
from app.schemas.company import CompanyCreate, CompanyRead

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
async def create_company(payload: CompanyCreate, db: AsyncSession = Depends(get_db)):
    return await CompanyRepository(db).create(payload.title)


@router.get("", response_model=list[CompanyRead])
async def list_companies(db: AsyncSession = Depends(get_db)):
    return await CompanyRepository(db).list()


@router.get("/by-code/{invite_code}", response_model=CompanyRead)
async def get_company_by_invite_code(invite_code: str, db: AsyncSession = Depends(get_db)):
    company = await CompanyRepository(db).get_by_invite_code(invite_code)
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return company


@router.get("/{company_id}", response_model=CompanyRead)
async def get_company(company_id: int, db: AsyncSession = Depends(get_db)):
    company = await CompanyRepository(db).get_by_id(company_id)
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return company


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(company_id: int, db: AsyncSession = Depends(get_db)) -> None:
    deleted = await CompanyRepository(db).delete(company_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
