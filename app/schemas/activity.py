from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ActivityResponse(BaseModel):
    id: int
    project_id: int
    actor_id: int
    action: str
    details: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ActivityListResponse(BaseModel):
    total_activities: int
    activities: list[ActivityResponse]
