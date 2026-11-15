from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.services.activity_service import log_activity
from app.database import get_db
from app.dependencies import get_current_user, require_roles
from app.models.models import Project, Revision, Quote, User
from app.schemas.quote import (
    QuoteCreateResponse,
    QuoteListResponse,
    QuoteStatusUpdateResponse
)
from app.services.notification_service import create_notification
from app.services.quote_service import (
    create_addon_quote,
    update_addon_quote_status
)

router = APIRouter(
    prefix="/projects/{project_id}/quotes",
    tags=["Add-on Quotes"]
)


class QuoteCreate(BaseModel):
    amount: float = Field(gt=0)
    description: str = Field(min_length=1)
    currency: str = Field(
        default="INR",
        min_length=3,
        max_length=3,
        pattern=r"^[A-Z]{3}$"
    )

    model_config = ConfigDict(str_strip_whitespace=True)


class QuoteStatusUpdate(BaseModel):
    status: Literal["ACCEPTED", "REJECTED"]


@router.post("/{revision_id}", response_model=QuoteCreateResponse)
def create_quote(
    project_id: int,
    revision_id: int,
    quote: QuoteCreate,
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

    revision = db.query(Revision).filter(
        Revision.id == revision_id,
        Revision.project_id == project_id
    ).first()

    if revision is None:
        raise HTTPException(404, "Revision not found")

    try:
        new_quote = create_addon_quote(
            db=db,
            project_id=project_id,
            revision=revision,
            amount=quote.amount,
            currency=quote.currency,
            description=quote.description
        )

        db.flush()

        log_activity(
            db=db,
            project_id=project_id,
            actor_id=current_user.id,
            action="QUOTE_CREATED",
            details=f"An add-on quote of {quote.amount} {quote.currency} was created."
        )

        create_notification(
            db=db,
            user_id=project.client_id,
            project_id=project_id,
            message=f"A new add-on quote is available for revision #{revision_id}."
        )

        db.commit()
        db.refresh(new_quote)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A quote already exists for this revision"
        )
    except Exception:
        db.rollback()
        raise

    return {
        "message": "Add-on quote created successfully",
        "quote": new_quote
    }


@router.get("/", response_model=QuoteListResponse)
def get_quotes(
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

    quotes = db.query(Quote).filter(
        Quote.project_id == project_id
    ).all()

    return {
        "total_quotes": len(quotes),
        "quotes": quotes
    }


@router.patch(
    "/{quote_id}/status",
    response_model=QuoteStatusUpdateResponse
)
def update_quote_status(
    project_id: int,
    quote_id: int,
    update: QuoteStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("CLIENT"))
):
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if project is None:
        raise HTTPException(404, "Project not found")

    if project.client_id != current_user.id:
        raise HTTPException(403, "You do not have access to this project")

    quote = db.query(Quote).filter(
        Quote.id == quote_id,
        Quote.project_id == project_id
    ).first()

    if quote is None:
        raise HTTPException(404, "Quote not found")

    try:
        updated_quote = update_addon_quote_status(
            db=db,
            quote=quote,
            new_status=update.status
        )

        log_activity(
            db=db,
            project_id=project_id,
            actor_id=current_user.id,
            action=f"QUOTE_{update.status}",
            details=f"Quote {quote_id} was {update.status.lower()}."
        )

        create_notification(
            db=db,
            user_id=project.freelancer_id,
            project_id=project_id,
            message=f"Your add-on quote #{quote_id} was {update.status.lower()}."
        )

        db.commit()
        db.refresh(updated_quote)

    except Exception:
        db.rollback()
        raise

    return {
        "message": "Quote status updated successfully",
        "quote": updated_quote
    }
