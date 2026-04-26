from __future__ import annotations

from typing import Any

from sqlalchemy import JSON, CheckConstraint, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class GameResult(Base):
    """The outcome of a participant in a game session."""

    __tablename__ = "game_result"
    __table_args__ = (
        CheckConstraint("char_length(trim(result_value)) > 0", name="game_result_value_not_blank"),
        Index("ix_game_result_game_session_id", "game_session_id"),
        Index("ix_game_result_participant_id", "participant_id"),
        UniqueConstraint("game_session_id", "participant_id", name="uq_game_result_session_participant"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    game_session_id: Mapped[int] = mapped_column(
        ForeignKey("game_session.id", ondelete="CASCADE"),
        nullable=False,
    )
    participant_id: Mapped[int] = mapped_column(
        ForeignKey("participant.id", ondelete="CASCADE"),
        nullable=False,
    )
    result_value: Mapped[str] = mapped_column(String(255), nullable=False)
    result_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    game_session: Mapped["GameSession"] = relationship(back_populates="results")
    participant: Mapped["Participant"] = relationship(back_populates="game_results")
