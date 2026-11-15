from sqlalchemy.orm import Session

from app.models.models import Notification


def create_notification(
    db: Session,
    user_id: int,
    project_id: int | None,
    message: str
):
    notification = Notification(
        user_id=user_id,
        project_id=project_id,
        message=message,
        is_read=False
    )

    # The calling route controls the transaction.
    db.add(notification)

    return notification
