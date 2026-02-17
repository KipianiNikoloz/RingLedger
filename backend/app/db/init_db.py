from app import models  # noqa: F401
from app.db.base import Base
from app.db.session import engine


def init_db() -> None:
    """Initialize database schema for local development."""
    Base.metadata.create_all(bind=engine)
