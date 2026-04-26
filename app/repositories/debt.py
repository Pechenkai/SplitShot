from __future__ import annotations

from decimal import Decimal

from sqlalchemy import delete, select

from app.db.models.debt import Debt
from app.repositories.base import BaseRepository


class DebtRepository(BaseRepository[Debt]):
    model = Debt

    async def create(self, company_id: int, debtor_id: int, creditor_id: int, amount: Decimal) -> Debt:
        debt = Debt(
            company_id=company_id,
            debtor_id=debtor_id,
            creditor_id=creditor_id,
            amount=amount,
        )
        return await self._save(debt)

    async def list_by_company(self, company_id: int) -> list[Debt]:
        stmt = select(Debt).where(Debt.company_id == company_id).order_by(Debt.id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_debtor(self, debtor_id: int) -> list[Debt]:
        stmt = select(Debt).where(Debt.debtor_id == debtor_id).order_by(Debt.id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_creditor(self, creditor_id: int) -> list[Debt]:
        stmt = select(Debt).where(Debt.creditor_id == creditor_id).order_by(Debt.id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_by_company(self, company_id: int) -> int:
        stmt = delete(Debt).where(Debt.company_id == company_id).returning(Debt.id)
        result = await self.session.execute(stmt)
        deleted_ids = list(result.scalars().all())
        await self._commit()
        return len(deleted_ids)

    async def delete(self, debt_id: int) -> bool:
        return await self.delete_by_id(debt_id)
