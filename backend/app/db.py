"""Database engine/session setup.

Points at the SQLite file produced by db/init_db.py (see docs/SOLUTION_ARCHITECTURE.md).
Using SQLAlchemy here specifically so a later swap to Postgres for a real
deployment is a config change, not a rewrite.
"""
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DB_PATH = Path(__file__).resolve().parent.parent.parent / "db" / "labor_planning.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
