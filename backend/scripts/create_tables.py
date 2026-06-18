from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db.management import run_schema_migrations


def main() -> None:
    print("Aplicando migraciones de la base de datos...", flush=True)
    run_schema_migrations()
    print("Esquema actualizado.")


if __name__ == "__main__":
    main()
