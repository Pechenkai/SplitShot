from __future__ import annotations

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TongueTwister(Base):
    __tablename__ = "tongue_twister"
    __table_args__ = (CheckConstraint("char_length(trim(text)) > 0", name="tongue_twister_text_not_blank"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String(500), nullable=False)


class Forfeit(Base):
    __tablename__ = "forfeit"
    __table_args__ = (
        CheckConstraint("char_length(trim(text)) > 0", name="forfeit_text_not_blank"),
        CheckConstraint("char_length(trim(kind)) > 0", name="forfeit_kind_not_blank"),
        Index("ix_forfeit_company_id", "company_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String(500), nullable=False)
    kind: Mapped[str] = mapped_column(String(32), nullable=False, default="built_in")
    company_id: Mapped[int | None] = mapped_column(ForeignKey("company.id", ondelete="CASCADE"), nullable=True)
