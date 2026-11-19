from datetime import datetime, timezone

from sqlalchemy import (
    String,
    Integer,
    DateTime,
    ForeignKey,
    Numeric,
    CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database import Base


class Quote(Base):
    __tablename__ = "quotes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    revision_request_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("revision_requests.id"),
        nullable=False,
        unique=True
    )

    amount: Mapped[float] = mapped_column(
        Numeric(10, 2),
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
            "amount >= 0",
            name="check_quote_amount"
        ),
        CheckConstraint(
            "status IN ('pending', 'accepted', 'rejected')",
            name="check_quote_status"
        ),
    )
