from __future__ import annotations

from typing import Generic, TypeVar

from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Small base repository with shared helpers."""

    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _commit(self) -> None:
        try:
            await self.session.commit()
        except SQLAlchemyError:
            await self.session.rollback()
            raise

    async def _save(self, instance: ModelT) -> ModelT:
        try:
            self.session.add(instance)
            await self.session.flush()
            await self.session.commit()
        except SQLAlchemyError:
            await self.session.rollback()
            raise

        await self.session.refresh(instance)
        return instance

    async def get_by_id(self, entity_id: int) -> ModelT | None:
        stmt = select(self.model).where(self.model.id == entity_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_by_id(self, entity_id: int) -> bool:
        try:
            stmt = delete(self.model).where(self.model.id == entity_id).returning(self.model.id)
            result = await self.session.execute(stmt)
            deleted_id = result.scalar_one_or_none()
            await self.session.commit()
        except SQLAlchemyError:
            await self.session.rollback()
            raise

        return deleted_id is not None
