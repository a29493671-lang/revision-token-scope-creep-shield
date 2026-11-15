from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session
from app.services.activity_service import log_activity

from app.database import get_db
from app.dependencies import require_roles, get_current_user
from app.models.models import Project, User
from app.schemas.project import (
    ProjectResponse,
    ProjectCreateResponse,
    ProjectListResponse
)

router = APIRouter(prefix="/projects", tags=["Projects"])


class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    client_email: str = Field(
        min_length=5,
        max_length=255,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    )

    model_config = ConfigDict(str_strip_whitespace=True)


@router.post("/", response_model=ProjectCreateResponse)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("FREELANCER"))
):
    client = db.query(User).filter(
        User.email == project.client_email.lower(),
        User.role == "CLIENT"
    ).first()

    if client is None:
        raise HTTPException(404, "Registered client not found")

    new_project = Project(
        title=project.title,
        description=project.description,
        client_name=client.name,
        client_id=client.id,
        freelancer_id=current_user.id
    )

    try:
        db.add(new_project)
        db.flush()

        log_activity(
            db=db,
            project_id=new_project.id,
            actor_id=current_user.id,
            action="PROJECT_CREATED",
            details=f"Project '{new_project.title}' was created."
        )

        db.commit()
        db.refresh(new_project)
    except Exception:
        db.rollback()
        raise

    return {
        "message": "Project created successfully",
        "project": new_project
    }


@router.get("/", response_model=ProjectListResponse)
def get_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "FREELANCER":
        query = db.query(Project).filter(
            Project.freelancer_id == current_user.id
        )
    else:
        query = db.query(Project).filter(
            Project.client_id == current_user.id
        )

    projects = query.all()

    return {
        "total_projects": len(projects),
        "projects": projects
    }


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if project is None:
        raise HTTPException(404, "Project not found")

    if current_user.id not in (
        project.freelancer_id,
        project.client_id
    ):
        raise HTTPException(403, "You do not have access to this project")

    return project
