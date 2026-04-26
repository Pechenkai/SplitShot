"""Add invite codes, game result data, and content tables.

Revision ID: 20260425_0002
Revises: 20260417_0001
Create Date: 2026-04-25 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260425_0002"
down_revision = "20260417_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("company", sa.Column("invite_code", sa.String(length=16), nullable=True))
    op.execute("UPDATE company SET invite_code = upper(substr(md5(random()::text || id::text), 1, 8))")
    op.alter_column("company", "invite_code", nullable=False)
    op.create_index("ix_company_invite_code", "company", ["invite_code"], unique=True)

    op.add_column("game_result", sa.Column("result_data", sa.JSON(), nullable=True))

    op.create_table(
        "tongue_twister",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("text", sa.String(length=500), nullable=False),
        sa.CheckConstraint("char_length(trim(text)) > 0", name="tongue_twister_text_not_blank"),
    )
    op.create_table(
        "forfeit",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("text", sa.String(length=500), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["company.id"], ondelete="CASCADE"),
        sa.CheckConstraint("char_length(trim(text)) > 0", name="forfeit_text_not_blank"),
        sa.CheckConstraint("char_length(trim(kind)) > 0", name="forfeit_kind_not_blank"),
    )
    op.create_index("ix_forfeit_company_id", "forfeit", ["company_id"])

    op.bulk_insert(
        sa.table("tongue_twister", sa.column("text", sa.String())),
        [
            {"text": "Карл у Клары украл кораллы, а Клара у Карла украла кларнет."},
            {"text": "Шла Саша по шоссе и сосала сушку."},
            {"text": "На дворе трава, на траве дрова."},
            {"text": "От топота копыт пыль по полю летит."},
        ],
    )
    op.bulk_insert(
        sa.table("forfeit", sa.column("text", sa.String()), sa.column("kind", sa.String())),
        [
            {"text": "Скажи тост за стол за 10 секунд.", "kind": "built_in"},
            {"text": "Изобрази официанта с самым серьезным лицом.", "kind": "built_in"},
            {"text": "Придумай новое название вашей компании.", "kind": "built_in"},
            {"text": "Сделай комплимент каждому участнику.", "kind": "built_in"},
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_forfeit_company_id", table_name="forfeit")
    op.drop_table("forfeit")
    op.drop_table("tongue_twister")
    op.drop_column("game_result", "result_data")
    op.drop_index("ix_company_invite_code", table_name="company")
    op.drop_column("company", "invite_code")
