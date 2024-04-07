import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def create_db_and_tables() -> None:
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    if "videos" not in tables or "fetch_history" not in tables:
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully.")
    else:
        print("Database tables already exist.")


def get_db() -> sessionmaker:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
