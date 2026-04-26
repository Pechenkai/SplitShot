from __future__ import annotations

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class GameResult(Base):
    """The outcome of a participant in a game session."""

    __tablename__ = "game_result"
    __table_args__ = (
        CheckConstraint("char_length(trim(result_value)) > 0", name="game_result_value_not_blank"),
        Index("ix_game_result_game_session_id", "game_session_id"),
        Index("ix_game_result_participant_id", "participant_id"),
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

    game_session: Mapped["GameSession"] = relationship(back_populates="results")
    participant: Mapped["Participant"] = relationship(back_populates="game_results")

