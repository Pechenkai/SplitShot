from __future__ import annotations

from sqlalchemy import func, or_, select

from app.db.models.content import Forfeit, TongueTwister
from app.repositories.base import BaseRepository


class TongueTwisterRepository(BaseRepository[TongueTwister]):
    model = TongueTwister

    async def create(self, text: str) -> TongueTwister:
        return await self._save(TongueTwister(text=text))

    async def random(self) -> TongueTwister | None:
        result = await self.session.execute(select(TongueTwister).order_by(func.random()).limit(1))
        return result.scalar_one_or_none()


class ForfeitRepository(BaseRepository[Forfeit]):
    model = Forfeit

    async def create_custom(self, company_id: int, text: str, kind: str = "custom") -> Forfeit:
        return await self._save(Forfeit(company_id=company_id, text=text, kind=kind))

    async def create_builtin(self, text: str, kind: str = "built_in") -> Forfeit:
        return await self._save(Forfeit(company_id=None, text=text, kind=kind))

    async def list_by_company(self, company_id: int) -> list[Forfeit]:
        stmt = (
            select(Forfeit)
            .where(or_(Forfeit.company_id.is_(None), Forfeit.company_id == company_id))
            .order_by(Forfeit.id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def random(self, company_id: int | None = None) -> Forfeit | None:
        stmt = select(Forfeit)
        if company_id is not None:
            stmt = stmt.where(or_(Forfeit.company_id.is_(None), Forfeit.company_id == company_id))
        else:
            stmt = stmt.where(Forfeit.company_id.is_(None))
        result = await self.session.execute(stmt.order_by(func.random()).limit(1))
        return result.scalar_one_or_none()
