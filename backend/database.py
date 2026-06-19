import os
from functools import lru_cache
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/travel_management")


class Base(DeclarativeBase):
    pass


@lru_cache
def get_engine():
    return create_engine(DATABASE_URL, echo=False)


@lru_cache
def get_sessionlocal():
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


def get_db():
    db = get_sessionlocal()()
    try:
        yield db
    finally:
        db.close()
