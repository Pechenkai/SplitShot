from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.check_item import CheckItemRepository
from app.repositories.company import CompanyRepository
from app.schemas.check_item import CheckItemCreate, CheckItemRead

router = APIRouter(tags=["check-items"])


@router.post("/companies/{company_id}/check-items", response_model=CheckItemRead, status_code=status.HTTP_201_CREATED)
async def create_check_item(company_id: int, payload: CheckItemCreate, db: AsyncSession = Depends(get_db)):
    if await CompanyRepository(db).get_by_id(company_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return await CheckItemRepository(db).create(company_id, payload.title, payload.price)


@router.get("/companies/{company_id}/check-items", response_model=list[CheckItemRead])
async def list_check_items(company_id: int, db: AsyncSession = Depends(get_db)):
    if await CompanyRepository(db).get_by_id(company_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return await CheckItemRepository(db).list_by_company(company_id)


@router.delete("/check-items/{check_item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_check_item(check_item_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await CheckItemRepository(db).delete(check_item_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Check item not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
