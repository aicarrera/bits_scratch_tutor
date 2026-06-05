from __future__ import annotations

import os
from pathlib import Path

import uvicorn


BASE_DIR = Path(__file__).resolve().parent


if __name__ == "__main__":
    os.chdir(BASE_DIR)
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[str(BASE_DIR / "app")],
    )
