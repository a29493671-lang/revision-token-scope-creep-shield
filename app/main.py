from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import engine
from app.models import models
from app.routers import projects, milestones, revisions, quotes, auth, activity, notifications
from app.schemas.common import HomeResponse, HealthResponse

# Create database tables on startup if they do not exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Revision Shield API",
    description="Freelance Revision Management System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(milestones.router)
app.include_router(revisions.router)
app.include_router(quotes.router)
app.include_router(auth.router)
app.include_router(activity.router)
app.include_router(notifications.router)


@app.get("/", response_model=HomeResponse)
def home():
    return {
        "message": "Welcome to Revision Shield Backend!"
    }


@app.get("/health", response_model=HealthResponse)
def health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "application": "Revision Shield",
            "database": "connected"
        }

    except SQLAlchemyError:
        return {
            "status": "unhealthy",
            "application": "Revision Shield",
            "database": "disconnected"
        }
