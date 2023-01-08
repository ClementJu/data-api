from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from app.config.config import settings

engine = create_engine(settings.DATABASE_URI, pool_pre_ping=True, connect_args={"check_same_thread": False})
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

if not inspect(engine).has_table("temporary_dialog_data"):
    Base.metadata.create_all(engine)


def get_db() -> Session:
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()
