from pydantic import BaseModel, ConfigDict


class ProjectResponse(BaseModel):
    id: int
    title: str
    description: str
    client_name: str

    model_config = ConfigDict(from_attributes=True)


class ProjectCreateResponse(BaseModel):
    message: str
    project: ProjectResponse


class ProjectListResponse(BaseModel):
    total_projects: int
    projects: list[ProjectResponse]
