from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select

from app.db.models.check_item import CheckItem
from app.repositories.base import BaseRepository


class CheckItemRepository(BaseRepository[CheckItem]):
    model = CheckItem

    async def create(self, company_id: int, title: str, price: Decimal) -> CheckItem:
        return await self._save(CheckItem(company_id=company_id, title=title, price=price))

    async def list_by_company(self, company_id: int) -> list[CheckItem]:
        stmt = select(CheckItem).where(CheckItem.company_id == company_id).order_by(CheckItem.id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(
        self,
        item_id: int,
        title: str | None = None,
        price: Decimal | None = None,
    ) -> CheckItem | None:
        item = await self.get_by_id(item_id)
        if item is None:
            return None

        if title is not None:
            item.title = title
        if price is not None:
            item.price = price

        await self._commit()
        await self.session.refresh(item)
        return item

    async def delete(self, item_id: int) -> bool:
        item = await self.get_by_id(item_id)
        if item is None:
            return False

        await self.session.delete(item)
        await self._commit()
        return True
