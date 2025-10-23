# app/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    os.environ.get("DATABASE_URL", f"postgresql://{os.environ.get('POSTGRES_USER','dd_user')}:{os.environ.get('POSTGRES_PASSWORD','NewStrongPass123!')}@localhost:5432/{os.environ.get('POSTGRES_DB','dd_db')}")
)

# Use future=True for SQLAlchemy 2.0 style
engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

def init_db():
    # import models so they register with Base
    import app.models  # noqa: F401
    # create tables
    Base.metadata.create_all(bind=engine)
