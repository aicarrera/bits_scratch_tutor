"""Add solution/reference fields to juegos.

Adds url_video, descripcion_solucion and bloques_clave to the juegos table so
the tutor prompt can use the reference solution and key blocks per game.
These columns already exist in the legacy Supabase database, so the statements
use IF NOT EXISTS to stay idempotent.

Revision ID: 0002_game_solution_fields
Revises: 0001_initial_schema
Create Date: 2026-07-16
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0002_game_solution_fields"
down_revision: str | None = "0001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TABLE juegos ADD COLUMN IF NOT EXISTS url_video TEXT")
    op.execute("ALTER TABLE juegos ADD COLUMN IF NOT EXISTS descripcion_solucion TEXT")
    op.execute("ALTER TABLE juegos ADD COLUMN IF NOT EXISTS bloques_clave TEXT")


def downgrade() -> None:
    op.execute("ALTER TABLE juegos DROP COLUMN IF EXISTS bloques_clave")
    op.execute("ALTER TABLE juegos DROP COLUMN IF EXISTS descripcion_solucion")
    op.execute("ALTER TABLE juegos DROP COLUMN IF EXISTS url_video")
