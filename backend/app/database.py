from sqlmodel import create_engine, Session
from pathlib import Path
from sqlalchemy import event

DATABASE_PATH = Path(__file__).resolve().parent.parent / "vanforge.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

# echo=True is helpful during development (logs SQL queries)
engine = create_engine(DATABASE_URL, echo=True)

@event.listens_for(engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

def get_session():
    with Session(engine) as session:
        yield session