"""Tests for SDK evaluators integration with the agent Judge."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add paths for imports
sdk_path = Path(__file__).parent.parent
project_root = sdk_path.parent
sys.path.insert(0, str(sdk_path))
sys.path.insert(0, str(project_root))


class TestJudgeEvaluator:
    """Tests for the JudgeEvaluator that wraps the agent Judge."""

    def test_evaluate_returns_result(self):
        """Test that evaluate returns a proper result dict."""
        from llm import MockLLMClient

        mock_llm = MockLLMClient()
        mock_llm.queue_response('''{
            "scores": {"accuracy": 5, "clarity": 4},
            "overall_score": 4,
            "strengths": ["Clear"],
            "weaknesses": [],
            "reasoning": "Good response"
        }''')

        from promptlab.evaluators import JudgeEvaluator

        evaluator = JudgeEvaluator(llm_client=mock_llm)
        result = evaluator.evaluate(
            output="Python is a programming language.",
            context={"input": "What is Python?"}
        )

        assert result["type"] == "judge"
        assert result["passed"] is True
        assert result["score"] == 8.0  # 4/5 * 10
        assert "reasoning" in result

    def test_evaluate_with_failing_response(self):
        """Test evaluation of a poor response."""
        from llm import MockLLMClient

        mock_llm = MockLLMClient()
        mock_llm.queue_response('''{
            "scores": {"accuracy": 1},
            "overall_score": 2,
            "strengths": [],
            "weaknesses": ["Incorrect"],
            "reasoning": "Wrong answer"
        }''')

        from promptlab.evaluators import JudgeEvaluator

        evaluator = JudgeEvaluator(llm_client=mock_llm)
        result = evaluator.evaluate(
            output="Python is a snake.",
            context={"input": "What is Python the programming language?"}
        )

        assert result["passed"] is False
        assert result["score"] < 6.0  # 2/5 * 10 = 4.0

    def test_evaluate_with_custom_rubric(self):
        """Test evaluation with custom rubric."""
        from llm import MockLLMClient

        mock_llm = MockLLMClient()
        mock_llm.queue_response('''{
            "scores": {"technical_accuracy": 5},
            "overall_score": 5,
            "strengths": ["Technically correct"],
            "weaknesses": [],
            "reasoning": "Perfect technical answer"
        }''')

        from promptlab.evaluators import JudgeEvaluator

        custom_rubric = "- Technical Accuracy: Is it technically correct?"
        evaluator = JudgeEvaluator(llm_client=mock_llm, rubric=custom_rubric)

        result = evaluator.evaluate(
            output="Recursion is when a function calls itself.",
            context={"input": "What is recursion?"}
        )

        assert result["passed"] is True
        # Verify custom rubric was used
        call = mock_llm.call_history[-1]
        assert "Technical Accuracy" in call["prompt"]

    def test_to_dict_serialization(self):
        """Test that evaluator can be serialized."""
        from llm import MockLLMClient
        from promptlab.evaluators import JudgeEvaluator

        evaluator = JudgeEvaluator(
            llm_client=MockLLMClient(),
            rubric="- Accuracy: Is it correct?"
        )

        data = evaluator.to_dict()

        assert data["type"] == "judge"
        assert data["rubric"] == "- Accuracy: Is it correct?"


class TestPairwiseEvaluator:
    """Tests for pairwise comparison evaluator."""

    def test_compare_returns_winner(self):
        """Test that compare returns a winner."""
        from llm import MockLLMClient

        mock_llm = MockLLMClient()
        mock_llm.queue_response('''{
            "winner": "B",
            "confidence": "high",
            "comparison": {},
            "reasoning": "B is more comprehensive"
        }''')

        from promptlab.evaluators import PairwiseEvaluator

        evaluator = PairwiseEvaluator(llm_client=mock_llm)
        result = evaluator.compare(
            input_text="What is Python?",
            output_a="A language.",
            output_b="Python is a high-level programming language."
        )

        assert result["winner"] == "B"
        assert result["confidence"] == "high"

    def test_compare_tie(self):
        """Test comparison resulting in tie."""
        from llm import MockLLMClient

        mock_llm = MockLLMClient()
        mock_llm.queue_response('''{
            "winner": "tie",
            "confidence": "medium",
            "comparison": {},
            "reasoning": "Both equally good"
        }''')

        from promptlab.evaluators import PairwiseEvaluator

        evaluator = PairwiseEvaluator(llm_client=mock_llm)
        result = evaluator.compare(
            input_text="Test",
            output_a="Response 1",
            output_b="Response 2"
        )

        assert result["winner"] == "tie"


class TestTrackedClientWithEvaluation:
    """Tests for tracked client with automatic evaluation."""

    def test_create_with_evaluation(self):
        """Test that tracked client can include evaluation."""
        from unittest.mock import MagicMock, patch
        from llm import MockLLMClient

        # Mock OpenAI response
        mock_openai_response = MagicMock()
        mock_openai_response.choices = [MagicMock()]
        mock_openai_response.choices[0].message.content = "Python is a programming language."
        mock_openai_response.usage.prompt_tokens = 10
        mock_openai_response.usage.completion_tokens = 5

        # Mock evaluation LLM
        eval_llm = MockLLMClient()
        eval_llm.queue_response('''{
            "scores": {"accuracy": 5},
            "overall_score": 5,
            "strengths": ["Correct"],
            "weaknesses": [],
            "reasoning": "Good"
        }''')

        from promptlab.evaluators import JudgeEvaluator

        evaluator = JudgeEvaluator(llm_client=eval_llm)

        # Evaluate the response
        result = evaluator.evaluate(
            output=mock_openai_response.choices[0].message.content,
            context={"input": "What is Python?"}
        )

        assert result["passed"] is True
        assert result["score"] == 10.0

    def test_evaluation_included_in_log_data(self):
        """Test that evaluation can be included in logged data."""
        from llm import MockLLMClient
        from promptlab.evaluators import JudgeEvaluator

        eval_llm = MockLLMClient()
        eval_llm.queue_response('''{
            "scores": {"accuracy": 4},
            "overall_score": 4,
            "strengths": ["Good"],
            "weaknesses": ["Minor issues"],
            "reasoning": "Mostly correct"
        }''')

        evaluator = JudgeEvaluator(llm_client=eval_llm)
        evaluation = evaluator.evaluate(
            output="Some response",
            context={"input": "Some input"}
        )

        # Build log data with evaluation
        log_data = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "Some input"}],
            "response_content": "Some response",
            "evaluation": evaluation,
        }

        assert "evaluation" in log_data
        assert log_data["evaluation"]["passed"] is True
        assert log_data["evaluation"]["score"] == 8.0


class TestContainsEvaluator:
    """Tests for the existing ContainsEvaluator."""

    def test_contains_evaluator_pass(self):
        """Test ContainsEvaluator when string is found."""
        from promptlab.evaluators import ContainsEvaluator

        evaluator = ContainsEvaluator(expected="Python")
        result = evaluator.evaluate(
            output="Python is a programming language.",
            context={}
        )

        assert result["passed"] is True
        assert result["score"] == 10

    def test_contains_evaluator_fail(self):
        """Test ContainsEvaluator when string is not found."""
        from promptlab.evaluators import ContainsEvaluator

        evaluator = ContainsEvaluator(expected="JavaScript")
        result = evaluator.evaluate(
            output="Python is a programming language.",
            context={}
        )

        assert result["passed"] is False
        assert result["score"] == 0

    def test_contains_evaluator_case_insensitive(self):
        """Test ContainsEvaluator with case insensitivity."""
        from promptlab.evaluators import ContainsEvaluator

        evaluator = ContainsEvaluator(expected="python", case_sensitive=False)
        result = evaluator.evaluate(
            output="Python is great!",
            context={}
        )

        assert result["passed"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
