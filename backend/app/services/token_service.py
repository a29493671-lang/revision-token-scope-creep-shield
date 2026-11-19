
from sqlalchemy.orm import Session

from backend.app.models import Milestone, RevisionRequest, Quote


def create_revision_request(
    db: Session,
    milestone_id: int,
    requested_by: int,
    description: str,
    quote_amount: float | None = None
):
    with db.begin():

        # Find the milestone
        milestone = db.get(Milestone, milestone_id)

        if milestone is None:
            raise ValueError("Milestone not found")

        # Check whether free revision tokens are available
        if milestone.remaining_revision_tokens > 0:

            # Create a free revision request
            revision_request = RevisionRequest(
                milestone_id=milestone_id,
                requested_by=requested_by,
                description=description,
                request_type="free",
                status="pending"
            )

            # Deduct one token
            milestone.remaining_revision_tokens -= 1

            db.add(revision_request)
            db.flush()

            result = {
                "message": "Free revision request created successfully",
                "request_type": "free",
                "remaining_tokens": milestone.remaining_revision_tokens,
                "revision_request_id": revision_request.id
            }

        else:

            # A quote amount is required for paid requests
            if quote_amount is None or quote_amount < 0:
                raise ValueError("A valid quote amount is required")

            # Create a paid revision request
            revision_request = RevisionRequest(
                milestone_id=milestone_id,
                requested_by=requested_by,
                description=description,
                request_type="paid",
                status="pending"
            )

            db.add(revision_request)
            db.flush()

            # Create its pending quote
            quote = Quote(
                revision_request_id=revision_request.id,
                amount=quote_amount,
                status="pending"
            )

            db.add(quote)

            result = {
                "message": "Paid revision request created successfully",
                "request_type": "paid",
                "remaining_tokens": 0,
                "revision_request_id": revision_request.id,
                "quote_amount": quote_amount,
                "quote_status": "pending"
            }

    return result
