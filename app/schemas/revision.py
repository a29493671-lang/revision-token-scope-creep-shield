from pydantic import BaseModel, ConfigDict


class RevisionResponse(BaseModel):
    id: int
    project_id: int
    milestone_id: int
    request_description: str
    revision_type: str
    status: str

    model_config = ConfigDict(from_attributes=True)


class RevisionCreateResponse(BaseModel):
    message: str
    revision: RevisionResponse
    tokens_remaining: int


class RevisionListResponse(BaseModel):
    total_revisions: int
    revisions: list[RevisionResponse]
