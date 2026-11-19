from pydantic import BaseModel


class HomeResponse(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str
    application: str
    database: str
