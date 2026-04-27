from __future__ import annotations

from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Debt(Base):
    """A debt record between two participants inside one company."""

    __tablename__ = "debt"
    __table_args__ = (
        CheckConstraint("amount >= 0", name="debt_amount_non_negative"),
        CheckConstraint("debtor_id <> creditor_id", name="debt_distinct_participants"),
        Index("ix_debt_company_id", "company_id"),
        Index("ix_debt_debtor_id", "debtor_id"),
        Index("ix_debt_creditor_id", "creditor_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("company.id", ondelete="CASCADE"), nullable=False)
    debtor_id: Mapped[int] = mapped_column(ForeignKey("participant.id", ondelete="CASCADE"), nullable=False)
    creditor_id: Mapped[int] = mapped_column(ForeignKey("participant.id", ondelete="CASCADE"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    company: Mapped["Company"] = relationship(back_populates="debts")
    debtor: Mapped["Participant"] = relationship(
        back_populates="debts_as_debtor",
        foreign_keys=[debtor_id],
    )
    creditor: Mapped["Participant"] = relationship(
        back_populates="debts_as_creditor",
        foreign_keys=[creditor_id],
    )
