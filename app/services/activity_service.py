from sqlalchemy.orm import Session

from app.models.models import ActivityLog


def log_activity(
    db: Session,
    project_id: int,
    actor_id: int | None,
    action: str,
    details: str = ""
):
    activity = ActivityLog(
        project_id=project_id,
        actor_id=actor_id,
        action=action,
        details=details
    )

    # Add to the current transaction.
    # The calling route is responsible for committing.
    db.add(activity)

    return activity
