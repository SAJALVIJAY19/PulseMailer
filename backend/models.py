import re

from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional, List
from uuid import UUID, uuid4
from datetime import datetime


def _check_meaningful(value: str, label: str, min_letters: int) -> str:
    value = value.strip()
    if not value:
        return value
    letters = [c for c in value if c.isalpha()]
    if len(letters) < min_letters:
        raise ValueError(f"{label} must contain at least {min_letters} letters")
    if re.search(r"(.)\1{3,}", value):
        raise ValueError(f"{label} looks like random characters")
    for word in re.findall(r"[A-Za-z]+", value):
        if len(word) >= 5 and not re.search(r"[aeiouyAEIOUY]", word):
            raise ValueError(f"{label} does not look like real text")
    return value


class CampaignRequest(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=100)
    brand_description: str = Field(
        default="", 
        max_length=500
    )
    tone: Literal["professional", "casual", "urgent", "friendly"]
    target_audience: str = Field(..., min_length=5)
    goal: Literal["awareness", "conversion", "retention", "re-engagement"]
    num_variants: int = Field(default=1, ge=1, le=5)
    schedule_weekly: bool = Field(default=False)

    @field_validator("product_name")
    @classmethod
    def validate_product_name(cls, v: str) -> str:
        return _check_meaningful(v, "Brand name", 2)

    @field_validator("target_audience")
    @classmethod
    def validate_target_audience(cls, v: str) -> str:
        return _check_meaningful(v, "Target audience", 4)

    @field_validator("brand_description")
    @classmethod
    def validate_brand_description(cls, v: str) -> str:
        return _check_meaningful(v, "Brand description", 5)


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
