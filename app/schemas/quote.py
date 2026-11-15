from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class QuoteResponse(BaseModel):
    id: int
    project_id: int
    revision_id: int
    amount: Decimal
    currency: str
    description: str
    status: str

    model_config = ConfigDict(from_attributes=True)


class QuoteCreateResponse(BaseModel):
    message: str
    quote: QuoteResponse


class QuoteListResponse(BaseModel):
    total_quotes: int
    quotes: list[QuoteResponse]


class QuoteStatusUpdateResponse(BaseModel):
    message: str
    quote: QuoteResponse
