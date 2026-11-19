from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session
from app.services.activity_service import log_activity
from app.database import get_db
from app.dependencies import get_current_user, require_roles
from app.models.models import Project, Milestone, User
from app.schemas.milestone import (
    MilestoneCreateResponse,
    MilestoneListResponse
)

router = APIRouter(
    prefix="/projects/{project_id}/milestones",
    tags=["Milestones"]
)


class MilestoneCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)

    model_config = ConfigDict(str_strip_whitespace=True)


@router.post("/", response_model=MilestoneCreateResponse)
def create_milestone(
    project_id: int,
    milestone: MilestoneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("FREELANCER"))
):
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if project is None:
        raise HTTPException(404, "Project not found")

    if project.freelancer_id != current_user.id:
        raise HTTPException(403, "You do not own this project")

    new_milestone = Milestone(
        project_id=project_id,
        title=milestone.title,
        description=milestone.description,
        tokens_total=3,
        tokens_remaining=3,
        status="ACTIVE"
    )

    try:
        db.add(new_milestone)
        db.flush()

        log_activity(
            db=db,
            project_id=project_id,
            actor_id=current_user.id,
            action="MILESTONE_CREATED",
            details=f"Milestone '{new_milestone.title}' was created."
        )

        db.commit()
        db.refresh(new_milestone)
    except Exception:
        db.rollback()
        raise

    return {
        "message": "Milestone created successfully",
        "milestone": new_milestone
    }


@router.get("/", response_model=MilestoneListResponse)
def get_milestones(
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

    milestones = db.query(Milestone).filter(
        Milestone.project_id == project_id
    ).all()

    return {
        "project_id": project_id,
        "total_milestones": len(milestones),
        "milestones": milestones
    }
