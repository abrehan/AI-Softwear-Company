import os

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker


if os.getenv("VERCEL"):
    DATABASE_URL = "sqlite:////tmp/virtual_office.db"
else:
    DATABASE_URL = "sqlite:///./virtual_office.db"


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def ensure_user_role_column() -> None:
    """Add role to older SQLite databases without deleting existing users."""
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("users")}
    if "role" in columns:
        return
    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'user'"))
        connection.execute(text("UPDATE users SET role = 'admin' WHERE id = (SELECT MIN(id) FROM users)"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
