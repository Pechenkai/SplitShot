from __future__ import annotations

from sqlalchemy import select

from app.db.models.participant import Participant
from app.repositories.base import BaseRepository


class ParticipantRepository(BaseRepository[Participant]):
    model = Participant

    async def create(self, company_id: int, name: str) -> Participant:
        return await self._save(Participant(company_id=company_id, name=name))

    async def list_by_company(self, company_id: int) -> list[Participant]:
        stmt = select(Participant).where(Participant.company_id == company_id).order_by(Participant.id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_name(self, participant_id: int, name: str) -> Participant | None:
        participant = await self.get_by_id(participant_id)
        if participant is None:
            return None

        participant.name = name
        await self._commit()
        await self.session.refresh(participant)
        return participant

    async def delete(self, participant_id: int) -> bool:
        return await self.delete_by_id(participant_id)
