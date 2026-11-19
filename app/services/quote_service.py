from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.models import Quote, Revision


def create_addon_quote(
    db: Session,
    project_id: int,
    revision: Revision,
    amount: float,
    currency: str,
    description: str
):
    if revision.project_id != project_id:
        raise HTTPException(
            status_code=400,
            detail="Revision does not belong to this project"
        )

    if revision.revision_type != "ADD_ON":
        raise HTTPException(
            status_code=400,
            detail="Quote can only be created for ADD_ON revisions"
        )

    existing_quote = db.query(Quote).filter(
        Quote.revision_id == revision.id
    ).first()

    if existing_quote:
        raise HTTPException(
            status_code=400,
            detail="A quote already exists for this revision"
        )

    new_quote = Quote(
        project_id=project_id,
        revision_id=revision.id,
        amount=amount,
        currency=currency,
        description=description,
        status="PENDING"
    )

    db.add(new_quote)
    return new_quote


def update_addon_quote_status(
    db: Session,
    quote: Quote,
    new_status: str
):
    if quote.status != "PENDING":
        raise HTTPException(
            status_code=400,
            detail="Only pending quotes can be updated"
        )

    quote.status = new_status
    return quote
