import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.engine import make_url
from sqlmodel import create_engine

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError("DATABASE_URL is not set")

DATABASE_URL = make_url(database_url).set(drivername="postgresql+psycopg")

engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
)