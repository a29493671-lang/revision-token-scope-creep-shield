from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.models import Project, ActivityLog, User
from app.schemas.activity import ActivityListResponse

router = APIRouter(
    prefix="/projects/{project_id}/activity",
    tags=["Activity Tracking"]
)


@router.get("/", response_model=ActivityListResponse)
def get_project_activity(
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
        raise HTTPException(
            403,
            "You do not have access to this project"
        )

    activities = db.query(ActivityLog).filter(
        ActivityLog.project_id == project_id
    ).order_by(
        ActivityLog.created_at.desc()
    ).all()

    return {
        "total_activities": len(activities),
        "activities": activities
    }
