from __future__ import annotations

from sqlalchemy import select

from app.db.models.game_session import GameSession
from app.repositories.base import BaseRepository


class GameSessionRepository(BaseRepository[GameSession]):
    model = GameSession

    async def create(self, company_id: int, game_type: str, status: str) -> GameSession:
        return await self._save(GameSession(company_id=company_id, game_type=game_type, status=status))

    async def list_by_company(self, company_id: int) -> list[GameSession]:
        stmt = select(GameSession).where(GameSession.company_id == company_id).order_by(GameSession.id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_status(self, session_id: int, status: str) -> GameSession | None:
        game_session = await self.get_by_id(session_id)
        if game_session is None:
            return None

        game_session.status = status
        await self._commit()
        await self.session.refresh(game_session)
        return game_session

    async def delete(self, session_id: int) -> bool:
        return await self.delete_by_id(session_id)
