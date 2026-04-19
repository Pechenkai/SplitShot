from __future__ import annotations

from sqlalchemy import select

from app.db.models.company import Company
from app.repositories.base import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    model = Company

    async def create(self, title: str) -> Company:
        return await self._save(Company(title=title))

    async def list_all(self) -> list[Company]:
        stmt = select(Company).order_by(Company.id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, company_id: int) -> bool:
        return await self.delete_by_id(company_id)

