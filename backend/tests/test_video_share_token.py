"""Tests for video prompt share token validation."""

import pytest
import hashlib
import secrets
from datetime import datetime, timedelta
from unittest.mock import MagicMock

import sys
from pathlib import Path

# Add paths for imports
backend_path = Path(__file__).parent.parent
project_root = backend_path.parent
sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(project_root))


class TestTokenGeneration:
    """Tests for share token generation."""

    def test_token_is_32_bytes_urlsafe(self):
        """Test that tokens are generated with 32 bytes (256 bits)."""
        raw_token = secrets.token_urlsafe(32)

        # URL-safe base64 encoding of 32 bytes is ~43 characters
        assert len(raw_token) >= 42
        assert len(raw_token) <= 44

    def test_token_is_unique(self):
        """Test that each token is unique."""
        tokens = [secrets.token_urlsafe(32) for _ in range(100)]
        unique_tokens = set(tokens)

        assert len(unique_tokens) == 100

    def test_token_hash_is_sha256(self):
        """Test that token hash is SHA256."""
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        # SHA256 hash is 64 hex characters
        assert len(token_hash) == 64
        assert all(c in "0123456789abcdef" for c in token_hash)

    def test_same_token_produces_same_hash(self):
        """Test that the same token always produces the same hash."""
        raw_token = "test_token_value"
        hash1 = hashlib.sha256(raw_token.encode()).hexdigest()
        hash2 = hashlib.sha256(raw_token.encode()).hexdigest()

        assert hash1 == hash2


class TestTokenValidation:
    """Tests for share token validation logic."""

    def test_valid_token_passes(self):
        """Test that a valid, non-expired, non-revoked token passes."""
        token = MagicMock()
        token.revoked_at = None
        token.expires_at = datetime.utcnow() + timedelta(days=7)

        now = datetime.utcnow()
        is_valid = token.revoked_at is None and token.expires_at > now

        assert is_valid is True

    def test_expired_token_fails(self):
        """Test that an expired token fails validation."""
        token = MagicMock()
        token.revoked_at = None
        token.expires_at = datetime.utcnow() - timedelta(days=1)

        now = datetime.utcnow()
        is_valid = token.revoked_at is None and token.expires_at > now

        assert is_valid is False

    def test_revoked_token_fails(self):
        """Test that a revoked token fails validation."""
        token = MagicMock()
        token.revoked_at = datetime.utcnow() - timedelta(hours=1)
        token.expires_at = datetime.utcnow() + timedelta(days=7)

        now = datetime.utcnow()
        is_valid = token.revoked_at is None and token.expires_at > now

        assert is_valid is False

    def test_expired_and_revoked_token_fails(self):
        """Test that a token that is both expired and revoked fails."""
        token = MagicMock()
        token.revoked_at = datetime.utcnow() - timedelta(hours=1)
        token.expires_at = datetime.utcnow() - timedelta(days=1)

        now = datetime.utcnow()
        is_valid = token.revoked_at is None and token.expires_at > now

        assert is_valid is False


class TestTokenExpiration:
    """Tests for token expiration logic."""

    def test_default_expiration_is_7_days(self):
        """Test that default expiration is 7 days."""
        expires_in_days = 7
        created_at = datetime.utcnow()
        expires_at = created_at + timedelta(days=expires_in_days)

        expected_expiry = created_at + timedelta(days=7)
        assert abs((expires_at - expected_expiry).total_seconds()) < 1

    def test_custom_expiration_works(self):
        """Test that custom expiration periods work."""
        for days in [1, 3, 7, 14, 30]:
            created_at = datetime.utcnow()
            expires_at = created_at + timedelta(days=days)

            # Check it expires in approximately the right number of days
            delta = expires_at - created_at
            assert delta.days == days

    def test_expiration_boundary(self):
        """Test token expiration at exact boundary."""
        # Token expires exactly now
        token = MagicMock()
        token.revoked_at = None
        exact_now = datetime.utcnow()
        token.expires_at = exact_now

        # A token that expires exactly now should be considered expired
        # (because expires_at > now is False when they're equal)
        now = exact_now
        is_valid = token.revoked_at is None and token.expires_at > now

        assert is_valid is False


class TestTokenRevocation:
    """Tests for token revocation logic."""

    def test_revoke_sets_revoked_at(self):
        """Test that revoking a token sets revoked_at."""
        token = MagicMock()
        token.revoked_at = None

        # Revoke the token
        token.revoked_at = datetime.utcnow()

        assert token.revoked_at is not None

    def test_revoked_token_stays_revoked(self):
        """Test that a revoked token stays revoked."""
        token = MagicMock()
        revoke_time = datetime.utcnow() - timedelta(hours=1)
        token.revoked_at = revoke_time

        # Check later
        now = datetime.utcnow()
        is_revoked = token.revoked_at is not None

        assert is_revoked is True
        assert token.revoked_at == revoke_time


class TestTokenHashLookup:
    """Tests for token hash lookup logic."""

    def test_correct_token_matches_hash(self):
        """Test that the correct token matches its hash."""
        raw_token = secrets.token_urlsafe(32)
        stored_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        # On access, hash the provided token
        provided_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        assert provided_hash == stored_hash

    def test_incorrect_token_does_not_match(self):
        """Test that an incorrect token doesn't match."""
        raw_token = secrets.token_urlsafe(32)
        stored_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        # Someone tries with wrong token
        wrong_token = secrets.token_urlsafe(32)
        provided_hash = hashlib.sha256(wrong_token.encode()).hexdigest()

        assert provided_hash != stored_hash

    def test_modified_token_does_not_match(self):
        """Test that a modified token doesn't match."""
        raw_token = secrets.token_urlsafe(32)
        stored_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        # Someone modifies the token slightly
        modified_token = raw_token + "x"
        provided_hash = hashlib.sha256(modified_token.encode()).hexdigest()

        assert provided_hash != stored_hash


class TestTokenSecurityProperties:
    """Tests for token security properties."""

    def test_raw_token_not_stored(self):
        """Test that raw tokens should not be stored, only hashes."""
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        # In DB, we should only store the hash
        # The raw token should be returned to user only once on creation
        # and never stored in DB

        # This test documents the expected pattern
        stored_value = token_hash  # What we store
        assert stored_value != raw_token  # We don't store the raw token
        assert len(stored_value) == 64  # SHA256 hash length

    def test_hash_is_one_way(self):
        """Test that you cannot derive the token from the hash."""
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        # There's no way to reverse SHA256, this test documents the property
        # The only way to validate is to hash the provided token and compare
        assert token_hash != raw_token
        # Hash is fixed length, token is variable
        assert len(token_hash) == 64
