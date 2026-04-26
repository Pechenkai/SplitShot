"""Initial schema for SplitShot DAL.

Revision ID: 20260417_0001
Revises:
Create Date: 2026-04-17 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260417_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "company",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("char_length(trim(title)) > 0", name="company_title_not_blank"),
    )

    op.create_table(
        "participant",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["company.id"], ondelete="CASCADE"),
        sa.CheckConstraint("char_length(trim(name)) > 0", name="participant_name_not_blank"),
    )
    op.create_index("ix_participant_company_id", "participant", ["company_id"])

    op.create_table(
        "check_item",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["company.id"], ondelete="CASCADE"),
        sa.CheckConstraint("price >= 0", name="check_item_price_non_negative"),
        sa.CheckConstraint("char_length(trim(title)) > 0", name="check_item_title_not_blank"),
    )
    op.create_index("ix_check_item_company_id", "check_item", ["company_id"])

    op.create_table(
        "debt",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("debtor_id", sa.Integer(), nullable=False),
        sa.Column("creditor_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["company.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["debtor_id"], ["participant.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["creditor_id"], ["participant.id"], ondelete="CASCADE"),
        sa.CheckConstraint("amount >= 0", name="debt_amount_non_negative"),
        sa.CheckConstraint("debtor_id <> creditor_id", name="debt_distinct_participants"),
    )
    op.create_index("ix_debt_company_id", "debt", ["company_id"])
    op.create_index("ix_debt_debtor_id", "debt", ["debtor_id"])
    op.create_index("ix_debt_creditor_id", "debt", ["creditor_id"])

    op.create_table(
        "game_session",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("game_type", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["company.id"], ondelete="CASCADE"),
        sa.CheckConstraint("char_length(trim(game_type)) > 0", name="game_session_game_type_not_blank"),
        sa.CheckConstraint("char_length(trim(status)) > 0", name="game_session_status_not_blank"),
    )
    op.create_index("ix_game_session_company_id", "game_session", ["company_id"])

    op.create_table(
        "game_result",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("game_session_id", sa.Integer(), nullable=False),
        sa.Column("participant_id", sa.Integer(), nullable=False),
        sa.Column("result_value", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(["game_session_id"], ["game_session.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["participant_id"], ["participant.id"], ondelete="CASCADE"),
        sa.CheckConstraint("char_length(trim(result_value)) > 0", name="game_result_value_not_blank"),
        sa.UniqueConstraint("game_session_id", "participant_id", name="uq_game_result_session_participant"),
    )
    op.create_index("ix_game_result_game_session_id", "game_result", ["game_session_id"])
    op.create_index("ix_game_result_participant_id", "game_result", ["participant_id"])


def downgrade() -> None:
    op.drop_index("ix_game_result_participant_id", table_name="game_result")
    op.drop_index("ix_game_result_game_session_id", table_name="game_result")
    op.drop_table("game_result")

    op.drop_index("ix_game_session_company_id", table_name="game_session")
    op.drop_table("game_session")

    op.drop_index("ix_debt_creditor_id", table_name="debt")
    op.drop_index("ix_debt_debtor_id", table_name="debt")
    op.drop_index("ix_debt_company_id", table_name="debt")
    op.drop_table("debt")

    op.drop_index("ix_check_item_company_id", table_name="check_item")
    op.drop_table("check_item")

    op.drop_index("ix_participant_company_id", table_name="participant")
    op.drop_table("participant")

    op.drop_table("company")
