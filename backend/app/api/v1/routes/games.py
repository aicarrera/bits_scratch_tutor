from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.games import GamesCatalogResponse
from app.services.games import GamesService

router = APIRouter()


@router.get("/", response_model=GamesCatalogResponse)
async def list_games(db: AsyncSession = Depends(get_db)) -> GamesCatalogResponse:
    return await GamesService(db).catalog()
