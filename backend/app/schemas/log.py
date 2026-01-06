from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class LogCreate(BaseModel):
    model: str = Field(..., max_length=100)
    provider: str = Field(..., max_length=50)
    messages: list[dict[str, Any]]
    parameters: dict[str, Any] | None = None
    response_content: str | None = None
    response_raw: dict[str, Any] | None = None
    latency_ms: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: Decimal | None = None
    prompt_slug: str | None = Field(None, max_length=255)
    tags: dict[str, Any] | None = None
    trace_id: str | None = Field(None, max_length=100)


class LogResponse(BaseModel):
    id: UUID
    org_id: UUID
    model: str
    provider: str
    messages: list[dict[str, Any]]
    parameters: dict[str, Any] | None
    response_content: str | None
    response_raw: dict[str, Any] | None
    latency_ms: int | None
    input_tokens: int | None
    output_tokens: int | None
    cost_usd: Decimal | None
    prompt_id: UUID | None
    tags: dict[str, Any] | None
    trace_id: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
