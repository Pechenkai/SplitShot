from __future__ import annotations

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Participant(Base):
    """A participant belonging to a company."""

    __tablename__ = "participant"
    __table_args__ = (
        CheckConstraint("char_length(trim(name)) > 0", name="participant_name_not_blank"),
        Index("ix_participant_company_id", "company_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("company.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    company: Mapped["Company"] = relationship(back_populates="participants")
    game_results: Mapped[list["GameResult"]] = relationship(
        back_populates="participant",
        passive_deletes=True,
    )
    debts_as_debtor: Mapped[list["Debt"]] = relationship(
        back_populates="debtor",
        foreign_keys="Debt.debtor_id",
        passive_deletes=True,
    )
    debts_as_creditor: Mapped[list["Debt"]] = relationship(
        back_populates="creditor",
        foreign_keys="Debt.creditor_id",
        passive_deletes=True,
    )
