from __future__ import annotations

from typing import Any

from app.db.models.game_result import GameResult
from app.db.models.game_session import GameSession
from app.repositories.game_result import GameResultRepository
from app.repositories.game_session import GameSessionRepository


class GameRepository:
    def __init__(self, session) -> None:
        self.sessions = GameSessionRepository(session)
        self.results = GameResultRepository(session)

    async def create_session(self, company_id: int, game_type: str, status: str = "created") -> GameSession:
        return await self.sessions.create(company_id, game_type, status)

    async def get_session(self, session_id: int) -> GameSession | None:
        return await self.sessions.get_by_id(session_id)

    async def list_sessions_by_company(self, company_id: int, limit: int = 100, offset: int = 0) -> list[GameSession]:
        return await self.sessions.list_by_company(company_id, limit=limit, offset=offset)

    async def set_session_status(self, session_id: int, status: str) -> GameSession | None:
        return await self.sessions.update_status(session_id, status)

    async def add_result(
        self,
        game_session_id: int,
        participant_id: int,
        result_value: str,
        result_data: dict[str, Any] | None = None,
    ) -> GameResult:
        return await self.results.create(game_session_id, participant_id, result_value, result_data)

    async def list_results(self, game_session_id: int, limit: int = 100, offset: int = 0) -> list[GameResult]:
        return await self.results.list_by_game_session(game_session_id, limit=limit, offset=offset)
