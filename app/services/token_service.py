from sqlalchemy import update
from sqlalchemy.orm import Session

from app.models.models import Milestone


def process_revision_token(
    db: Session,
    milestone: Milestone
):
    result = db.execute(
        update(Milestone)
        .where(
            Milestone.id == milestone.id,
            Milestone.tokens_remaining > 0
        )
        .values(
            tokens_remaining=Milestone.tokens_remaining - 1
        )
    )

    if result.rowcount == 1:
        db.refresh(milestone)

        return {
            "revision_type": "FREE_TOKEN",
            "status": "APPROVED",
            "tokens_remaining": milestone.tokens_remaining
        }

    return {
        "revision_type": "ADD_ON",
        "status": "QUOTE_REQUIRED",
        "tokens_remaining": 0
    }
