"""Judge evaluator that uses the agent Judge for LLM-based evaluation."""

import sys
from pathlib import Path
from typing import Any

from .base import BaseEvaluator

# Add project root to path for agent imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


class JudgeEvaluator(BaseEvaluator):
    """
    Evaluator that uses the agent Judge for LLM-based evaluation.

    Uses a rubric to score responses on multiple criteria.
    """

    def __init__(
        self,
        llm_client: Any = None,
        rubric: str | None = None,
        model: str = "gpt-4o-mini",
    ):
        """
        Initialize the judge evaluator.

        Args:
            llm_client: LLM client to use. Creates OpenAIClient if not provided.
            rubric: Custom evaluation rubric. Uses default if not provided.
            model: Model to use for evaluation.
        """
        self.rubric = rubric
        self.model = model

        if llm_client is None:
            from llm import OpenAIClient
            self._llm_client = OpenAIClient()
        else:
            self._llm_client = llm_client

    def evaluate(self, output: str, context: dict[str, Any]) -> dict[str, Any]:
        """
        Evaluate an output using the Judge agent.

        Args:
            output: The LLM output to evaluate.
            context: Additional context. Should contain 'input' key with original request.

        Returns:
            Dict with evaluation results.
        """
        from agents import Judge

        judge = Judge(self._llm_client, model=self.model, rubric=self.rubric)

        input_text = context.get("input", "")
        judgment = judge.evaluate(input_text, output)

        # Convert score from 1-5 to 0-10 scale
        score = (judgment.overall_score / 5) * 10

        return {
            "type": "judge",
            "passed": judgment.passed,
            "score": score,
            "scores": judgment.scores,
            "strengths": judgment.strengths,
            "weaknesses": judgment.weaknesses,
            "reasoning": judgment.reasoning,
        }

    def to_dict(self) -> dict[str, Any]:
        """Serialize the evaluator for API/storage."""
        return {
            "type": "judge",
            "rubric": self.rubric,
            "model": self.model,
        }


class PairwiseEvaluator(BaseEvaluator):
    """
    Evaluator that compares two outputs to determine which is better.
    """

    def __init__(
        self,
        llm_client: Any = None,
        rubric: str | None = None,
        model: str = "gpt-4o-mini",
    ):
        """
        Initialize the pairwise evaluator.

        Args:
            llm_client: LLM client to use. Creates OpenAIClient if not provided.
            rubric: Custom evaluation rubric. Uses default if not provided.
            model: Model to use for evaluation.
        """
        self.rubric = rubric
        self.model = model

        if llm_client is None:
            from llm import OpenAIClient
            self._llm_client = OpenAIClient()
        else:
            self._llm_client = llm_client

    def evaluate(self, output: str, context: dict[str, Any]) -> dict[str, Any]:
        """
        Not used for pairwise comparison. Use compare() instead.
        """
        raise NotImplementedError("Use compare() for pairwise evaluation")

    def compare(
        self,
        input_text: str,
        output_a: str,
        output_b: str,
    ) -> dict[str, Any]:
        """
        Compare two outputs to determine which is better.

        Args:
            input_text: The original input/request.
            output_a: First output to compare.
            output_b: Second output to compare.

        Returns:
            Dict with comparison results.
        """
        from agents import Judge

        judge = Judge(self._llm_client, model=self.model, rubric=self.rubric)
        result = judge.compare(input_text, output_a, output_b)

        return {
            "type": "pairwise",
            "winner": result.winner,
            "confidence": result.confidence,
            "comparison": result.comparison,
            "reasoning": result.reasoning,
        }

    def to_dict(self) -> dict[str, Any]:
        """Serialize the evaluator for API/storage."""
        return {
            "type": "pairwise",
            "rubric": self.rubric,
            "model": self.model,
        }
