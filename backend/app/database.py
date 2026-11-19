
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

# Get the main project directory
BASE_DIR = Path(__file__).resolve().parents[2]

# Database file location
DATABASE_PATH = BASE_DIR / "revision_shield.db"

# SQLite database URL
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

# Create database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for database models
Base = declarative_base()


# Database connection dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Test database connection
def check_database_connection():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("Database connected successfully!")
        return True

    except Exception as error:
        print("Database connection failed:", error)
        return False



def create_tables():
    # Import all models so SQLAlchemy knows about them
    from backend.app import models

    # Create all database tables
    Base.metadata.create_all(bind=engine)

    print("All database tables created successfully!")

