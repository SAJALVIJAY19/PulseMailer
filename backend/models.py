from pydantic import BaseModel, Field
from typing import Literal, Optional, List
from uuid import UUID, uuid4
from datetime import datetime


class CampaignRequest(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=100)
    tone: Literal["professional", "casual", "urgent", "friendly"]
    target_audience: str = Field(..., min_length=5)
    goal: Literal["awareness", "conversion", "retention", "re-engagement"]
    num_variants: int = Field(default=1, ge=1, le=5)
    schedule_weekly: bool = Field(default=False)


class GeneratedEmail(BaseModel):
    subject_line: str = Field(..., min_length=1, max_length=78)
    body: str = Field(..., min_length=50)
    cta_text: str
    tokens_used: int = Field(default=0)


class CampaignResponse(BaseModel):
    campaign_id: UUID = Field(default_factory=uuid4)
    product_name: str
    emails: List[GeneratedEmail]
    cached: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    error_code: str
    message: str
    field: Optional[str] = None
