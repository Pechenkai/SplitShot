from __future__ import annotations

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class GameSession(Base):
    """A playable session recorded for a company."""

    __tablename__ = "game_session"
    __table_args__ = (
        CheckConstraint("char_length(trim(game_type)) > 0", name="game_session_game_type_not_blank"),
        CheckConstraint("char_length(trim(status)) > 0", name="game_session_status_not_blank"),
        Index("ix_game_session_company_id", "company_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("company.id", ondelete="CASCADE"), nullable=False)
    game_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)

    company: Mapped["Company"] = relationship(back_populates="game_sessions")
    results: Mapped[list["GameResult"]] = relationship(
        back_populates="game_session",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

