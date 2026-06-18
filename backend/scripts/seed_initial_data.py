import asyncio
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db.management import seed_initial_data


def main() -> None:
    print("Cargando datos iniciales...", flush=True)
    asyncio.run(seed_initial_data())
    print("Datos iniciales cargados.")


if __name__ == "__main__":
    main()
