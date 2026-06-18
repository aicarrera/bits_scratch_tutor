from pathlib import Path

from alembic import command
from alembic.config import Config

from app.db.database import AsyncSessionLocal
from app.db.seed import seed_demo_data

_BACKEND_DIR = Path(__file__).resolve().parents[2]


def build_alembic_config() -> Config:
    config = Config(str(_BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(_BACKEND_DIR / "alembic"))
    return config


def run_schema_migrations() -> None:
    command.upgrade(build_alembic_config(), "head")


async def seed_initial_data() -> None:
    async with AsyncSessionLocal() as session:
        await seed_demo_data(session)
