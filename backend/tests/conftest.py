"""Pytest fixtures for backend tests."""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

# Add paths for imports
backend_path = Path(__file__).parent.parent
project_root = backend_path.parent
sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(project_root))


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    db = AsyncMock()
    return db


@pytest.fixture
def mock_org():
    """Create a mock organization."""
    org = MagicMock()
    org.id = "test-org-id"
    org.name = "Test Org"
    return org


@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client."""
    from llm import MockLLMClient
    return MockLLMClient()


@pytest.fixture
def skill_registry():
    """Create a skill registry."""
    from prompts import SkillRegistry
    return SkillRegistry()
