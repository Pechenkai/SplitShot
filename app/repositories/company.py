from __future__ import annotations

import secrets
import string

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db.models.company import Company
from app.repositories.base import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    model = Company

    async def create(self, title: str) -> Company:
        for _ in range(5):
            try:
                return await self._save(Company(title=title, invite_code=await self._make_invite_code()))
            except IntegrityError:
                await self.session.rollback()

        return await self._save(Company(title=title, invite_code=await self._make_invite_code()))

    async def _make_invite_code(self) -> str:
        alphabet = string.ascii_uppercase + string.digits
        while True:
            code = "".join(secrets.choice(alphabet) for _ in range(8))
            if await self.get_by_invite_code(code) is None:
                return code

    async def get_by_invite_code(self, invite_code: str) -> Company | None:
        stmt = select(Company).where(Company.invite_code == invite_code)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Company]:
        stmt = select(Company).order_by(Company.id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list(self) -> list[Company]:
        return await self.list_all()

    async def delete(self, company_id: int) -> bool:
        return await self.delete_by_id(company_id)
