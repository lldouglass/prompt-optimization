"""Authentication schemas for request/response validation."""

from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class RegisterRequest(BaseModel):
    """Request to register a new user."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    name: str | None = Field(None, max_length=255)
    organization_name: str = Field(..., min_length=1, max_length=255)


class LoginRequest(BaseModel):
    """Request to log in with email/password."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User information response."""
    id: UUID
    email: str
    name: str | None
    avatar_url: str | None
    email_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class OrganizationBasicResponse(BaseModel):
    """Basic organization info for auth responses."""
    id: UUID
    name: str
    subscription_plan: str

    model_config = {"from_attributes": True}


class MembershipResponse(BaseModel):
    """User's membership in an organization."""
    organization: OrganizationBasicResponse
    role: str

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    """Response after successful authentication."""
    user: UserResponse
    memberships: list[MembershipResponse]
    current_organization: OrganizationBasicResponse | None = None


class MessageResponse(BaseModel):
    """Simple message response."""
    message: str


class VerifyEmailRequest(BaseModel):
    """Request to verify email with token."""
    token: str


class ResendVerificationRequest(BaseModel):
    """Request to resend verification email."""
    email: EmailStr
