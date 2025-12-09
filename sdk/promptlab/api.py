import httpx
from typing import Any


class PromptLabAPI:
    """Client for PromptLab backend API."""

    DEFAULT_BASE_URL = "http://localhost:8000"

    def __init__(
        self,
        api_key: str,
        base_url: str | None = None,
        timeout: float = 10.0,
    ):
        self.api_key = api_key
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=timeout,
        )

    def log_request(self, data: dict[str, Any]) -> dict[str, Any] | None:
        """Log a request to the backend. Fire and forget - errors are swallowed."""
        try:
            response = self._client.post("/api/v1/logs", json=data)
            response.raise_for_status()
            return response.json()
        except Exception:
            # Don't fail user's code if logging fails
            return None

    def get_prompt(self, slug: str) -> dict[str, Any]:
        """Fetch a prompt by slug."""
        response = self._client.get(f"/api/v1/prompts/{slug}")
        response.raise_for_status()
        return response.json()

    def run_tests(self, suite_id: str, prompt_version_id: str) -> dict[str, Any]:
        """Trigger a test run."""
        response = self._client.post(
            f"/api/v1/suites/{suite_id}/run",
            json={"prompt_version_id": prompt_version_id},
        )
        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self) -> "PromptLabAPI":
        return self

    def __exit__(self, *args) -> None:
        self.close()
