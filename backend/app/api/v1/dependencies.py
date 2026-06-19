from fastapi import Header, HTTPException, status

from app.core.settings import get_settings


async def require_admin_code(x_admin_code: str | None = Header(default=None)) -> None:
    settings = get_settings()
    if x_admin_code != settings.admin_finish_code:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Código de administrador inválido.")
