from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os


DEFAULT_SQLITE_URL = "sqlite:///./project.db"


def _build_engine(database_url: str):
    if database_url.startswith("sqlite"):
        return create_engine(database_url, connect_args={"check_same_thread": False})
    return create_engine(database_url)


SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_SQLITE_URL)

engine = _build_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
