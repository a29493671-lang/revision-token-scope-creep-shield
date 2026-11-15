from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session
from app.services.activity_service import log_activity
from app.database import get_db
from app.dependencies import get_current_user, require_roles
from app.models.models import Project, Milestone, Revision, User
from app.schemas.revision import (
    RevisionCreateResponse,
    RevisionListResponse
)
from app.services.token_service import process_revision_token
from app.services.notification_service import create_notification

router = APIRouter(
    prefix="/projects/{project_id}/milestones/{milestone_id}/revisions",
    tags=["Revisions"]
)


class RevisionCreate(BaseModel):
    request_description: str = Field(min_length=1)

    model_config = ConfigDict(str_strip_whitespace=True)


@router.post("/", response_model=RevisionCreateResponse)
def create_revision(
    project_id: int,
    milestone_id: int,
    revision: RevisionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("CLIENT"))
):
    milestone = db.query(Milestone).filter(
        Milestone.id == milestone_id,
        Milestone.project_id == project_id
    ).first()

    if milestone is None:
        raise HTTPException(404, "Milestone not found")

    if milestone.project.client_id != current_user.id:
        raise HTTPException(403, "You do not have access to this project")

    try:
        token_result = process_revision_token(db, milestone)

        new_revision = Revision(
            project_id=project_id,
            milestone_id=milestone_id,
            request_description=revision.request_description,
            revision_type=token_result["revision_type"],
            status=token_result["status"]
        )

        db.add(new_revision)
        db.flush()

        log_activity(
            db=db,
            project_id=project_id,
            actor_id=current_user.id,
            action="REVISION_REQUESTED",
            details="A new revision request was submitted."
        )

        create_notification(
            db=db,
            user_id=milestone.project.freelancer_id,
            project_id=project_id,
            message=f"A new revision request was submitted for milestone '{milestone.title}'."
        )

        db.commit()
        db.refresh(new_revision)
        db.refresh(milestone)

    except Exception:
        db.rollback()
        raise

    return {
        "message": "Revision request submitted successfully",
        "revision": new_revision,
        "tokens_remaining": milestone.tokens_remaining
    }


@router.get("/", response_model=RevisionListResponse)
def get_revisions(
    project_id: int,
    milestone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    milestone = db.query(Milestone).filter(
        Milestone.id == milestone_id,
        Milestone.project_id == project_id
    ).first()

    if milestone is None:
        raise HTTPException(404, "Milestone not found")

    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if project is None or current_user.id not in (
        project.freelancer_id,
        project.client_id
    ):
        raise HTTPException(403, "You do not have access to this project")

    revisions = db.query(Revision).filter(
        Revision.project_id == project_id,
        Revision.milestone_id == milestone_id
    ).all()

    return {
        "total_revisions": len(revisions),
        "revisions": revisions
    }
