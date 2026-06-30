"""Add url_video column to juegos.

Revision ID: 0002_add_url_video_juegos
Revises: 0001_initial_schema
Create Date: 2026-06-30
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_add_url_video_juegos"
down_revision: str | None = "0001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _has_column(table: str, column: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return any(col["name"] == column for col in inspector.get_columns(table))


def upgrade() -> None:
    # Idempotent: the column may already have been added manually in some envs.
    if not _has_column("juegos", "url_video"):
        op.add_column("juegos", sa.Column("url_video", sa.Text(), nullable=True))


def downgrade() -> None:
    if _has_column("juegos", "url_video"):
        op.drop_column("juegos", "url_video")
