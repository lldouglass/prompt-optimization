import os
import time
import threading
from typing import Any

from .api import PromptLabAPI


class PromptLab:
    """Main PromptLab client."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        self.api_key = api_key or os.getenv("PROMPTLAB_API_KEY")
        if not self.api_key:
            raise ValueError(
                "PROMPTLAB_API_KEY not set. Pass api_key or set the environment variable."
            )
        self.api = PromptLabAPI(self.api_key, base_url=base_url)

    def track_openai(self, client: Any) -> "TrackedOpenAI":
        """Wrap an OpenAI client to enable tracking."""
        return TrackedOpenAI(client, self.api)


def track(
    client: Any,
    api_key: str | None = None,
    base_url: str | None = None,
) -> Any:
    """Convenience function to wrap any supported client."""
    # Import here to avoid requiring openai if not used
    try:
        from openai import OpenAI
    except ImportError:
        OpenAI = None

    lab = PromptLab(api_key, base_url=base_url)

    if OpenAI and isinstance(client, OpenAI):
        return lab.track_openai(client)
    else:
        raise TypeError(f"Unsupported client type: {type(client)}")


class TrackedOpenAI:
    """OpenAI client wrapper with automatic logging."""

    def __init__(self, client: Any, api: PromptLabAPI):
        self._client = client
        self._api = api
        self.chat = TrackedChat(client.chat, api)

    def __getattr__(self, name: str) -> Any:
        # Pass through non-tracked methods
        return getattr(self._client, name)


class TrackedChat:
    """Wrapper for OpenAI chat namespace."""

    def __init__(self, chat: Any, api: PromptLabAPI):
        self._chat = chat
        self._api = api
        self.completions = TrackedCompletions(chat.completions, api)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._chat, name)


class TrackedCompletions:
    """Wrapper for OpenAI chat.completions with logging."""

    def __init__(self, completions: Any, api: PromptLabAPI):
        self._completions = completions
        self._api = api

    def create(
        self,
        *,
        prompt_slug: str | None = None,
        tags: dict[str, Any] | None = None,
        trace_id: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Create a chat completion with automatic logging."""
        start_time = time.time()

        # Make the actual API call
        response = self._completions.create(**kwargs)

        latency_ms = int((time.time() - start_time) * 1000)

        # Build log data
        log_data = {
            "model": kwargs.get("model"),
            "provider": "openai",
            "messages": kwargs.get("messages"),
            "parameters": {
                k: v
                for k, v in kwargs.items()
                if k not in ["model", "messages"]
            },
            "response_content": response.choices[0].message.content if response.choices else None,
            "latency_ms": latency_ms,
            "input_tokens": response.usage.prompt_tokens if response.usage else None,
            "output_tokens": response.usage.completion_tokens if response.usage else None,
            "prompt_slug": prompt_slug,
            "tags": tags,
            "trace_id": trace_id,
        }

        # Fire and forget - log in background thread
        threading.Thread(
            target=self._api.log_request,
            args=(log_data,),
            daemon=True,
        ).start()

        return response

    def __getattr__(self, name: str) -> Any:
        return getattr(self._completions, name)
