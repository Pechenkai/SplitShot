from __future__ import annotations

from sqlalchemy import select

from app.db.models.game_result import GameResult
from app.repositories.base import BaseRepository


class GameResultRepository(BaseRepository[GameResult]):
    model = GameResult

    async def create(self, game_session_id: int, participant_id: int, result_value: str) -> GameResult:
        game_result = GameResult(
            game_session_id=game_session_id,
            participant_id=participant_id,
            result_value=result_value,
        )
        return await self._save(game_result)

    async def list_by_game_session(self, game_session_id: int) -> list[GameResult]:
        stmt = select(GameResult).where(GameResult.game_session_id == game_session_id).order_by(GameResult.id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_participant(self, participant_id: int) -> list[GameResult]:
        stmt = select(GameResult).where(GameResult.participant_id == participant_id).order_by(GameResult.id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, result_id: int) -> bool:
        return await self.delete_by_id(result_id)

