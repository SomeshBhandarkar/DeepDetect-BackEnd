
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    os.environ.get("DATABASE_URL", f"postgresql://{os.environ.get('POSTGRES_USER','dd_user')}:{os.environ.get('POSTGRES_PASSWORD','NewStrongPass123!')}@localhost:5432/{os.environ.get('POSTGRES_DB','dd_db')}")
)


engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

def init_db():

    import app.models 

    Base.metadata.create_all(bind=engine)

