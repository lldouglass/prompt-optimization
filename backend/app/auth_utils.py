"""Authentication utilities for password hashing and session tokens."""

import secrets
import hashlib
from passlib.context import CryptContext

# Password hashing context using Argon2
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using Argon2."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def generate_session_token() -> str:
    """Generate a cryptographically secure session token."""
    return secrets.token_urlsafe(32)


def hash_session_token(token: str) -> str:
    """Hash a session token for storage (SHA256 is fine for random tokens)."""
    return hashlib.sha256(token.encode()).hexdigest()


def generate_verification_token() -> str:
    """Generate a cryptographically secure email verification token."""
    return secrets.token_urlsafe(32)
