"""Bootstrap the local mock data source for the Labor Planning Tool.

Creates (or resets) labor_planning.db from schema.sql, then loads seed_data.sql.
Run from the repo root or from this directory: `python db/init_db.py`.

This database is a stand-in for real WMS/WFM/OMS-fed tables -- see
docs/SOLUTION_ARCHITECTURE.md. It is not intended to become a production
data store.
"""
import sqlite3
import sys
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent
DB_PATH = DB_DIR / "labor_planning.db"
SCHEMA_PATH = DB_DIR / "schema.sql"
SEED_PATH = DB_DIR / "seed_data.sql"


def main() -> None:
    reset = "--reset" in sys.argv
    if DB_PATH.exists() and not reset:
        print(
            f"{DB_PATH.name} already exists. Re-run with --reset to drop and "
            "re-seed it, to avoid silently duplicating rows."
        )
        sys.exit(1)

    if DB_PATH.exists() and reset:
        DB_PATH.unlink()
        print(f"Removed existing {DB_PATH.name}.")

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(SCHEMA_PATH.read_text())
        conn.executescript(SEED_PATH.read_text())
        conn.commit()
    finally:
        conn.close()

    print(f"Created and seeded {DB_PATH} from {SCHEMA_PATH.name} + {SEED_PATH.name}.")


if __name__ == "__main__":
    main()
