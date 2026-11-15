from pydantic import BaseModel, ConfigDict


class MilestoneResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: str
    tokens_total: int
    tokens_remaining: int
    status: str

    model_config = ConfigDict(from_attributes=True)


class MilestoneCreateResponse(BaseModel):
    message: str
    milestone: MilestoneResponse


class MilestoneListResponse(BaseModel):
    project_id: int
    total_milestones: int
    milestones: list[MilestoneResponse]
