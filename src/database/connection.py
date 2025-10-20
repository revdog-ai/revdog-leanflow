"""
Database connection and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import structlog

from src.database.models import Base
from backend.core.config import settings

logger = structlog.get_logger()

# Create engine
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite-specific configuration
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # PostgreSQL or other databases
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Initialize database (create all tables)."""
    logger.info("Initializing database")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully")


def get_db() -> Generator[Session, None, None]:
    """
    Get database session.
    
    Yields:
        SQLAlchemy session
        
    Usage:
        db = next(get_db())
        try:
            # Use db
        finally:
            db.close()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session() -> Session:
    """
    Get database session (direct).
    
    Returns:
        SQLAlchemy session
        
    Note: Remember to close the session after use.
    """
    return SessionLocal()

