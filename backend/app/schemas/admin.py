from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


# Organization schemas
class OrganizationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class OrganizationResponse(BaseModel):
    id: UUID
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}


# API Key schemas
class ApiKeyCreate(BaseModel):
    name: str | None = Field(None, max_length=255)


class ApiKeyResponse(BaseModel):
    id: UUID
    key_prefix: str
    name: str | None
    created_at: datetime
    last_used_at: datetime | None

    model_config = {"from_attributes": True}


class ApiKeyCreateResponse(ApiKeyResponse):
    """Response when creating a new API key - includes the raw key (only shown once)."""
    key: str = Field(..., description="The full API key. Save this - it won't be shown again!")
