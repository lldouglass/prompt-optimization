from abc import ABC, abstractmethod
from typing import Any


class BaseEvaluator(ABC):
    """Base class for all evaluators."""

    @abstractmethod
    def evaluate(self, output: str, context: dict[str, Any]) -> dict[str, Any]:
        """
        Evaluate an output.

        Args:
            output: The LLM output to evaluate
            context: Additional context (input, variables, etc.)

        Returns:
            Dict with keys:
                - type: evaluator type name
                - passed: bool indicating if evaluation passed
                - score: float from 0-10
                - reasoning: optional explanation
        """
        pass

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Serialize for API/storage."""
        pass
