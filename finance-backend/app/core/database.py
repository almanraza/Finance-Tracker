from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from loguru import logger

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,          # Max connections in pool
    max_overflow=20,       # Extra connections allowed beyond pool_size
    pool_pre_ping=True,    # Check connection health before using
    pool_recycle=3600,     # Recycle connections every hour
    echo=settings.APP_ENV == "development",  # Log SQL in dev only
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency — yields DB session, always closes on exit."""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()
