"""Schemas for user feedback endpoints."""

from pydantic import BaseModel, Field
from typing import Optional


class FeedbackCreateRequest(BaseModel):
    """Request to create user feedback on an evaluation or comparison."""

    feedback_type: str = Field(
        ...,
        description="Either 'evaluation' or 'comparison'"
    )
    agrees_with_result: Optional[bool] = Field(
        None,
        description="Whether user agrees with the agent's judgment/comparison result"
    )
    quality_rating: Optional[int] = Field(
        None,
        ge=1,
        le=10,
        description="User's rating of the result quality (1-10)"
    )
    comment: Optional[str] = Field(
        None,
        max_length=2000,
        description="Optional free-form feedback comment"
    )
    saved_evaluation_id: Optional[str] = Field(
        None,
        description="UUID of the saved evaluation if feedback is on a saved item"
    )
    context_snapshot: Optional[dict] = Field(
        None,
        description="Snapshot of the evaluation/comparison data at time of feedback"
    )


class FeedbackResponse(BaseModel):
    """Response containing saved feedback."""

    id: str
    feedback_type: str
    agrees_with_result: Optional[bool] = None
    quality_rating: Optional[int] = None
    comment: Optional[str] = None
    saved_evaluation_id: Optional[str] = None
    created_at: str


class FeedbackListResponse(BaseModel):
    """Response containing list of feedback items."""

    feedback: list[FeedbackResponse]
    total: int
