"""
LLM Client Abstraction Layer

Provides a pluggable interface for LLM API calls.
Actual implementations can be swapped in later.
"""

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from pathlib import Path

import openai
from dotenv import load_dotenv

# Load .env file - check multiple locations
_env_locations = [
    Path.cwd() / ".env",
    Path.cwd() / "backend" / ".env",
    Path(__file__).parent.parent / ".env",
    Path(__file__).parent.parent / "backend" / ".env",
]
for _env_path in _env_locations:
    if _env_path.exists():
        load_dotenv(_env_path)
        break


# =============================================================================
# Token usage tracking
# =============================================================================

_usage_tracker = {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0,
    "call_count": 0,
}


def get_usage() -> dict[str, int]:
    """Get the current token usage since last reset."""
    return _usage_tracker.copy()


def reset_usage() -> dict[str, int]:
    """Reset the usage tracker and return the final counts."""
    global _usage_tracker
    final = _usage_tracker.copy()
    _usage_tracker = {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "call_count": 0,
    }
    return final


def calculate_cost_cents(prompt_tokens: int, completion_tokens: int, model: str = "gpt-4o-mini") -> int:
    """Calculate estimated cost in cents (hundredths of a dollar).

    Pricing for gpt-4o-mini:
    - Input: $0.15 per 1M tokens = $0.00000015 per token
    - Output: $0.60 per 1M tokens = $0.0000006 per token
    """
    if "gpt-4o-mini" in model:
        input_cost = prompt_tokens * 0.00000015
        output_cost = completion_tokens * 0.0000006
    else:
        # Default to gpt-4o pricing for other models
        input_cost = prompt_tokens * 0.0000025
        output_cost = completion_tokens * 0.00001

    total_dollars = input_cost + output_cost
    return int(total_dollars * 100)  # Convert to cents


# =============================================================================
# Simple chat() function interface (for Judge agent compatibility)
# =============================================================================

def chat(model: str, messages: list[dict[str, str]]) -> str:
    """
    Simple chat function interface for LLM calls.

    Args:
        model: Model identifier (e.g., "gpt-4o-mini").
        messages: List of message dicts with 'role' and 'content'.

    Returns:
        The assistant's response content as a string.

    Raises:
        NotImplementedError: If no API key is configured.

    Example:
        >>> response = chat("gpt-4o-mini", [{"role": "user", "content": "Hello"}])
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise NotImplementedError(
            "LLM client not wired up yet. Set OPENAI_API_KEY environment variable "
            "or implement llm.client.chat() with your preferred provider."
        )

    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.2,
    )

    # Track token usage
    if response.usage:
        _usage_tracker["prompt_tokens"] += response.usage.prompt_tokens
        _usage_tracker["completion_tokens"] += response.usage.completion_tokens
        _usage_tracker["total_tokens"] += response.usage.total_tokens
        _usage_tracker["call_count"] += 1

    return response.choices[0].message.content or ""


@dataclass
class LLMResponse:
    """Response from an LLM API call."""

    content: str
    model: str
    usage: dict[str, int] = field(default_factory=dict)
    finish_reason: str = "stop"
    raw_response: Any = None

    @property
    def total_tokens(self) -> int:
        """Total tokens used (prompt + completion)."""
        return self.usage.get("total_tokens", 0)


class LLMClient(ABC):
    """
    Abstract base class for LLM clients.

    Implement this interface to plug in different LLM providers
    (OpenAI, Anthropic, local models, etc.)
    """

    @abstractmethod
    def complete(
        self,
        prompt: str,
        *,
        model: str = "gpt-4.1",
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Generate a completion for the given prompt.

        Args:
            prompt: The prompt text to complete.
            model: Model identifier to use.
            max_tokens: Maximum tokens in the response.
            temperature: Sampling temperature (0-2).
            **kwargs: Additional provider-specific parameters.

        Returns:
            LLMResponse with the generated content.
        """
        pass

    @abstractmethod
    def complete_chat(
        self,
        messages: list[dict[str, str]],
        *,
        model: str = "gpt-4.1",
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Generate a completion for a chat conversation.

        Args:
            messages: List of message dicts with 'role' and 'content'.
            model: Model identifier to use.
            max_tokens: Maximum tokens in the response.
            temperature: Sampling temperature (0-2).
            **kwargs: Additional provider-specific parameters.

        Returns:
            LLMResponse with the generated content.
        """
        pass


class MockLLMClient(LLMClient):
    """
    Mock LLM client for testing and development.

    Returns configurable mock responses.
    """

    def __init__(self, default_response: str = "This is a mock response."):
        """
        Initialize the mock client.

        Args:
            default_response: Default response text to return.
        """
        self.default_response = default_response
        self.call_history: list[dict[str, Any]] = []
        self._response_queue: list[str] = []

    def queue_response(self, response: str) -> None:
        """Queue a response to be returned on the next call."""
        self._response_queue.append(response)

    def queue_responses(self, responses: list[str]) -> None:
        """Queue multiple responses."""
        self._response_queue.extend(responses)

    def complete(
        self,
        prompt: str,
        *,
        model: str = "gpt-4.1",
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> LLMResponse:
        """Return a mock completion."""
        self.call_history.append({
            "method": "complete",
            "prompt": prompt,
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "kwargs": kwargs,
        })

        content = (
            self._response_queue.pop(0)
            if self._response_queue
            else self.default_response
        )

        return LLMResponse(
            content=content,
            model=model,
            usage={
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(content.split()),
                "total_tokens": len(prompt.split()) + len(content.split()),
            },
        )

    def complete_chat(
        self,
        messages: list[dict[str, str]],
        *,
        model: str = "gpt-4.1",
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> LLMResponse:
        """Return a mock chat completion."""
        self.call_history.append({
            "method": "complete_chat",
            "messages": messages,
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "kwargs": kwargs,
        })

        content = (
            self._response_queue.pop(0)
            if self._response_queue
            else self.default_response
        )

        # Estimate tokens from messages
        prompt_tokens = sum(
            len(m.get("content", "").split()) for m in messages
        )

        return LLMResponse(
            content=content,
            model=model,
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": len(content.split()),
                "total_tokens": prompt_tokens + len(content.split()),
            },
        )

    def reset(self) -> None:
        """Reset call history and response queue."""
        self.call_history.clear()
        self._response_queue.clear()


class OpenAIClient(LLMClient):
    """
    OpenAI LLM client implementation.

    Uses the OpenAI API to generate completions.
    """

    def __init__(
        self,
        api_key: str | None = None,
        default_model: str = "gpt-4o-mini",
    ):
        """
        Initialize the OpenAI client.

        Args:
            api_key: OpenAI API key. If not provided, uses OPENAI_API_KEY env var.
            default_model: Default model to use for completions.

        Raises:
            ValueError: If no API key is provided or found in environment.
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key is required. Provide it via api_key parameter "
                "or set the OPENAI_API_KEY environment variable."
            )
        self.default_model = default_model
        self._client = openai.OpenAI(api_key=self.api_key)

    def complete(
        self,
        prompt: str,
        *,
        model: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Generate a completion for the given prompt.

        Converts the prompt to a chat message and calls the chat completions API.
        """
        model = model or self.default_model
        messages = [{"role": "user", "content": prompt}]

        response = self._client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs,
        )

        return LLMResponse(
            content=response.choices[0].message.content or "",
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            finish_reason=response.choices[0].finish_reason or "stop",
            raw_response=response,
        )

    def complete_chat(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Generate a completion for a chat conversation.
        """
        model = model or self.default_model

        response = self._client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs,
        )

        return LLMResponse(
            content=response.choices[0].message.content or "",
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            finish_reason=response.choices[0].finish_reason or "stop",
            raw_response=response,
        )
