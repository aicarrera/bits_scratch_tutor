from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.games import GamesRepository
from app.schemas.games import GamesCatalogResponse
from app.services.serializers import serialize_category, serialize_game


class GamesService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = GamesRepository(db)

    async def catalog(self) -> GamesCatalogResponse:
        categories = await self.repo.list_active_categories()
        categories_by_id = {category.id: category for category in categories}
        games = await self.repo.list_active_games()
        return GamesCatalogResponse(
            categorias=[serialize_category(category) for category in categories],
            juegos=[
                serialize_game(game, await self.repo.get_active_version(game.id), categories_by_id.get(game.categoria_id or ""))
                for game in games
            ],
        )
