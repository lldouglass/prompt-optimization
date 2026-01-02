"""Pytest fixtures for agent optimization tests."""

import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client."""
    from llm import MockLLMClient
    return MockLLMClient()
