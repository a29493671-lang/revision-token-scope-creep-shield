
from datetime import datetime, timezone
from sqlalchemy import (
    String,
    Integer,
    DateTime,
    ForeignKey,
    Text,
    CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database import Base


class RevisionRequest(Base):
    __tablename__ = "revision_requests"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    milestone_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("milestones.id"),
        nullable=False
    )

    requested_by: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    request_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        CheckConstraint(
            "request_type IN ('free', 'paid')",
            name="check_revision_request_type"
        ),
        CheckConstraint(
            "status IN ('pending', 'approved', 'rejected', 'completed')",
            name="check_revision_request_status"
        ),
    )
