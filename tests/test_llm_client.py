"""Tests for LLM client implementations."""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from llm import LLMResponse, MockLLMClient


class TestLLMResponse:
    """Tests for LLMResponse dataclass."""

    def test_total_tokens_property(self):
        response = LLMResponse(
            content="Hello",
            model="gpt-4o-mini",
            usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        )
        assert response.total_tokens == 15

    def test_total_tokens_empty_usage(self):
        response = LLMResponse(content="Hello", model="gpt-4o-mini")
        assert response.total_tokens == 0

    def test_default_finish_reason(self):
        response = LLMResponse(content="Hello", model="gpt-4o-mini")
        assert response.finish_reason == "stop"


class TestMockLLMClient:
    """Tests for MockLLMClient."""

    def test_default_response(self):
        client = MockLLMClient()
        response = client.complete("test")
        assert response.content == "This is a mock response."

    def test_custom_default_response(self):
        client = MockLLMClient(default_response="Custom response")
        response = client.complete("test")
        assert response.content == "Custom response"

    def test_queue_response(self):
        client = MockLLMClient()
        client.queue_response("First response")
        response = client.complete("test")
        assert response.content == "First response"

    def test_queue_multiple_responses(self):
        client = MockLLMClient()
        client.queue_responses(["First", "Second", "Third"])
        assert client.complete("test").content == "First"
        assert client.complete("test").content == "Second"
        assert client.complete("test").content == "Third"

    def test_call_history(self):
        client = MockLLMClient()
        client.complete("test prompt", model="gpt-4", max_tokens=100, temperature=0.5)

        assert len(client.call_history) == 1
        call = client.call_history[0]
        assert call["method"] == "complete"
        assert call["prompt"] == "test prompt"
        assert call["model"] == "gpt-4"
        assert call["max_tokens"] == 100
        assert call["temperature"] == 0.5

    def test_reset(self):
        client = MockLLMClient()
        client.queue_response("test")
        client.complete("test")

        client.reset()

        assert len(client.call_history) == 0
        assert len(client._response_queue) == 0


class TestOpenAIClient:
    """Tests for OpenAIClient with mocked OpenAI library."""

    @pytest.fixture
    def mock_openai_response(self):
        """Create a mock OpenAI API response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Mock OpenAI response"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.model = "gpt-4o-mini"
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15
        return mock_response

    def test_init_with_api_key(self):
        """Test initialization with explicit API key."""
        with patch("llm.client.openai") as mock_openai:
            from llm import OpenAIClient
            client = OpenAIClient(api_key="test-key")
            mock_openai.OpenAI.assert_called_once_with(api_key="test-key")

    def test_init_with_env_var(self):
        """Test initialization with environment variable."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "env-key"}):
            with patch("llm.client.openai") as mock_openai:
                from llm import OpenAIClient
                client = OpenAIClient()
                mock_openai.OpenAI.assert_called_once_with(api_key="env-key")

    def test_init_missing_api_key(self):
        """Test that missing API key raises error."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove OPENAI_API_KEY if it exists
            os.environ.pop("OPENAI_API_KEY", None)
            with patch("llm.client.openai"):
                from llm import OpenAIClient
                with pytest.raises(ValueError, match="API key"):
                    OpenAIClient()

    def test_complete_basic(self, mock_openai_response):
        """Test basic completion."""
        with patch("llm.client.openai") as mock_openai:
            mock_openai.OpenAI.return_value.chat.completions.create.return_value = mock_openai_response

            from llm import OpenAIClient
            client = OpenAIClient(api_key="test-key")
            response = client.complete("Hello, world!")

            assert response.content == "Mock OpenAI response"
            assert response.model == "gpt-4o-mini"
            assert response.usage["total_tokens"] == 15

            # Verify API was called correctly
            mock_openai.OpenAI.return_value.chat.completions.create.assert_called_once()
            call_kwargs = mock_openai.OpenAI.return_value.chat.completions.create.call_args[1]
            assert call_kwargs["messages"] == [{"role": "user", "content": "Hello, world!"}]

    def test_complete_with_parameters(self, mock_openai_response):
        """Test completion with custom parameters."""
        with patch("llm.client.openai") as mock_openai:
            mock_openai.OpenAI.return_value.chat.completions.create.return_value = mock_openai_response

            from llm import OpenAIClient
            client = OpenAIClient(api_key="test-key")
            response = client.complete(
                "Test prompt",
                model="gpt-4-turbo",
                max_tokens=500,
                temperature=0.2,
            )

            call_kwargs = mock_openai.OpenAI.return_value.chat.completions.create.call_args[1]
            assert call_kwargs["model"] == "gpt-4-turbo"
            assert call_kwargs["max_tokens"] == 500
            assert call_kwargs["temperature"] == 0.2

    def test_complete_chat_basic(self, mock_openai_response):
        """Test chat completion."""
        with patch("llm.client.openai") as mock_openai:
            mock_openai.OpenAI.return_value.chat.completions.create.return_value = mock_openai_response

            from llm import OpenAIClient
            client = OpenAIClient(api_key="test-key")

            messages = [
                {"role": "system", "content": "You are helpful."},
                {"role": "user", "content": "Hello!"},
            ]
            response = client.complete_chat(messages)

            assert response.content == "Mock OpenAI response"

            call_kwargs = mock_openai.OpenAI.return_value.chat.completions.create.call_args[1]
            assert call_kwargs["messages"] == messages

    def test_complete_chat_with_parameters(self, mock_openai_response):
        """Test chat completion with custom parameters."""
        with patch("llm.client.openai") as mock_openai:
            mock_openai.OpenAI.return_value.chat.completions.create.return_value = mock_openai_response

            from llm import OpenAIClient
            client = OpenAIClient(api_key="test-key")

            messages = [{"role": "user", "content": "Test"}]
            response = client.complete_chat(
                messages,
                model="gpt-4",
                max_tokens=2048,
                temperature=0.8,
            )

            call_kwargs = mock_openai.OpenAI.return_value.chat.completions.create.call_args[1]
            assert call_kwargs["model"] == "gpt-4"
            assert call_kwargs["max_tokens"] == 2048
            assert call_kwargs["temperature"] == 0.8

    def test_default_model(self, mock_openai_response):
        """Test that default model is gpt-4o-mini."""
        with patch("llm.client.openai") as mock_openai:
            mock_openai.OpenAI.return_value.chat.completions.create.return_value = mock_openai_response

            from llm import OpenAIClient
            client = OpenAIClient(api_key="test-key")
            client.complete("Test")

            call_kwargs = mock_openai.OpenAI.return_value.chat.completions.create.call_args[1]
            assert call_kwargs["model"] == "gpt-4o-mini"

    def test_custom_default_model(self, mock_openai_response):
        """Test initialization with custom default model."""
        with patch("llm.client.openai") as mock_openai:
            mock_openai.OpenAI.return_value.chat.completions.create.return_value = mock_openai_response

            from llm import OpenAIClient
            client = OpenAIClient(api_key="test-key", default_model="gpt-4-turbo")
            client.complete("Test")

            call_kwargs = mock_openai.OpenAI.return_value.chat.completions.create.call_args[1]
            assert call_kwargs["model"] == "gpt-4-turbo"

    def test_raw_response_preserved(self, mock_openai_response):
        """Test that raw OpenAI response is preserved."""
        with patch("llm.client.openai") as mock_openai:
            mock_openai.OpenAI.return_value.chat.completions.create.return_value = mock_openai_response

            from llm import OpenAIClient
            client = OpenAIClient(api_key="test-key")
            response = client.complete("Test")

            assert response.raw_response is mock_openai_response

    def test_extra_kwargs_passed(self, mock_openai_response):
        """Test that extra kwargs are passed to OpenAI API."""
        with patch("llm.client.openai") as mock_openai:
            mock_openai.OpenAI.return_value.chat.completions.create.return_value = mock_openai_response

            from llm import OpenAIClient
            client = OpenAIClient(api_key="test-key")
            client.complete("Test", top_p=0.9, presence_penalty=0.5)

            call_kwargs = mock_openai.OpenAI.return_value.chat.completions.create.call_args[1]
            assert call_kwargs["top_p"] == 0.9
            assert call_kwargs["presence_penalty"] == 0.5


class TestOpenAIClientErrorHandling:
    """Tests for OpenAI client error handling."""

    def test_api_error_propagates(self):
        """Test that API errors are propagated."""
        with patch("llm.client.openai") as mock_openai:
            mock_openai.OpenAI.return_value.chat.completions.create.side_effect = Exception("API Error")

            from llm import OpenAIClient
            client = OpenAIClient(api_key="test-key")

            with pytest.raises(Exception, match="API Error"):
                client.complete("Test")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
