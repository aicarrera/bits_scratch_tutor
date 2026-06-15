from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Game, GameCategory, GameVersion


class GamesRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_active_categories(self) -> list[GameCategory]:
        result = await self.db.scalars(
            select(GameCategory).where(GameCategory.activo.is_(True)).order_by(GameCategory.orden, GameCategory.nombre)
        )
        return list(result)

    async def list_active_games(self) -> list[Game]:
        result = await self.db.scalars(select(Game).where(Game.activo.is_(True)).order_by(Game.id))
        return list(result)

    async def get_active_version(self, game_id: str) -> GameVersion | None:
        return await self.db.scalar(
            select(GameVersion)
            .where(GameVersion.juego_id == game_id, GameVersion.activo.is_(True))
            .order_by(GameVersion.creado_en.desc())
        )

    async def get_game(self, game_id: str) -> Game | None:
        return await self.db.get(Game, game_id)
