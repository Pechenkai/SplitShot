from __future__ import annotations

from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CheckItem(Base):
    """A bill line item for a company."""

    __tablename__ = "check_item"
    __table_args__ = (
        CheckConstraint("price >= 0", name="check_item_price_non_negative"),
        CheckConstraint("char_length(trim(title)) > 0", name="check_item_title_not_blank"),
        Index("ix_check_item_company_id", "company_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company_id: Mapped[int] = mapped_column(ForeignKey("company.id", ondelete="CASCADE"), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    company: Mapped["Company"] = relationship(back_populates="check_items")

