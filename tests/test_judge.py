"""Tests for the Judge agent."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents import Judge, Judgment, PairwiseJudgment, LegacyJudge
from llm import MockLLMClient


@pytest.fixture
def mock_llm():
    """Create a mock LLM client."""
    return MockLLMClient()


@pytest.fixture
def judge(mock_llm):
    """Create a legacy judge with mock LLM for backward-compatible tests."""
    return LegacyJudge(mock_llm)


class TestJudgment:
    """Tests for Judgment dataclass."""

    def test_passed_threshold(self):
        """Test that passed is True for scores >= 3."""
        judgment = Judgment(overall_score=3)
        assert judgment.passed is True

        judgment = Judgment(overall_score=5)
        assert judgment.passed is True

    def test_failed_threshold(self):
        """Test that passed is False for scores < 3."""
        judgment = Judgment(overall_score=2)
        assert judgment.passed is False

        judgment = Judgment(overall_score=0)
        assert judgment.passed is False

    def test_default_values(self):
        """Test default values for Judgment."""
        judgment = Judgment()
        assert judgment.scores == {}
        assert judgment.overall_score == 0
        assert judgment.strengths == []
        assert judgment.weaknesses == []


class TestPairwiseJudgment:
    """Tests for PairwiseJudgment dataclass."""

    def test_create_judgment(self):
        """Test creating a pairwise judgment."""
        judgment = PairwiseJudgment(
            winner="A",
            confidence="high",
            reasoning="A is better",
        )
        assert judgment.winner == "A"
        assert judgment.confidence == "high"

    def test_tie_result(self):
        """Test tie result."""
        judgment = PairwiseJudgment(
            winner="tie",
            confidence="medium",
        )
        assert judgment.winner == "tie"


class TestJudge:
    """Tests for the Judge agent."""

    def test_evaluate_good_response(self, judge, mock_llm):
        """Test evaluating a good response."""
        mock_llm.queue_response('''{
            "scores": {
                "accuracy": 5,
                "completeness": 4,
                "clarity": 5,
                "helpfulness": 4
            },
            "overall_score": 5,
            "strengths": ["Accurate", "Well-organized"],
            "weaknesses": ["Could be more detailed"],
            "reasoning": "Good response overall"
        }''')

        result = judge.evaluate(
            "What is Python?",
            "Python is a high-level programming language.",
        )

        assert result.overall_score == 5
        assert result.passed is True
        assert result.scores["accuracy"] == 5
        assert len(result.strengths) == 2
        assert len(result.weaknesses) == 1

    def test_evaluate_poor_response(self, judge, mock_llm):
        """Test evaluating a poor response."""
        mock_llm.queue_response('''{
            "scores": {
                "accuracy": 1,
                "completeness": 1,
                "clarity": 2,
                "helpfulness": 1
            },
            "overall_score": 1,
            "strengths": [],
            "weaknesses": ["Inaccurate", "Incomplete", "Not helpful"],
            "reasoning": "Response is incorrect and unhelpful"
        }''')

        result = judge.evaluate("What is Python?", "Python is a snake.")

        assert result.overall_score == 1
        assert result.passed is False
        assert len(result.weaknesses) >= 1

    def test_evaluate_fallback_on_invalid_json(self, judge, mock_llm):
        """Test fallback when JSON parsing fails."""
        mock_llm.queue_response("Invalid JSON response")

        result = judge.evaluate("Test", "Test response")

        assert result.overall_score == 0
        assert "Failed to parse" in result.weaknesses[0]

    def test_compare_clear_winner(self, judge, mock_llm):
        """Test pairwise comparison with clear winner."""
        mock_llm.queue_response('''{
            "winner": "B",
            "confidence": "high",
            "comparison": {
                "accuracy": {"winner": "tie", "explanation": "Both correct"},
                "completeness": {"winner": "B", "explanation": "More detail"}
            },
            "reasoning": "B provides more comprehensive answer"
        }''')

        result = judge.compare(
            "What is Python?",
            "A programming language.",
            "Python is a high-level, interpreted programming language known for readability.",
        )

        assert result.winner == "B"
        assert result.confidence == "high"
        assert result.comparison["completeness"]["winner"] == "B"

    def test_compare_tie(self, judge, mock_llm):
        """Test pairwise comparison resulting in tie."""
        mock_llm.queue_response('''{
            "winner": "tie",
            "confidence": "medium",
            "comparison": {},
            "reasoning": "Both responses are equally good"
        }''')

        result = judge.compare("Test", "Response 1", "Response 2")

        assert result.winner == "tie"
        assert result.confidence == "medium"

    def test_compare_fallback_on_invalid_json(self, judge, mock_llm):
        """Test fallback when pairwise JSON parsing fails."""
        mock_llm.queue_response("Not valid JSON")

        result = judge.compare("Test", "A", "B")

        assert result.winner == "tie"
        assert result.confidence == "low"
        assert "Failed to parse" in result.reasoning

    def test_custom_rubric(self, mock_llm):
        """Test judge with custom rubric."""
        custom_rubric = """
        - Technical Accuracy: Is the code correct?
        - Performance: Is the solution efficient?
        """
        judge = LegacyJudge(mock_llm, rubric=custom_rubric)

        mock_llm.queue_response('''{
            "scores": {"technical_accuracy": 5, "performance": 4},
            "overall_score": 4,
            "strengths": [],
            "weaknesses": [],
            "reasoning": "Good code"
        }''')

        result = judge.evaluate("Fix this bug", "Here's the fix...")

        # Verify custom rubric was used in the prompt
        last_call = mock_llm.call_history[-1]
        assert "Technical Accuracy" in last_call["prompt"]
        assert "Performance" in last_call["prompt"]

    def test_llm_parameters(self, judge, mock_llm):
        """Test that correct LLM parameters are used."""
        mock_llm.queue_response('{"overall_score": 3}')

        judge.evaluate("Test", "Test response")

        call = mock_llm.call_history[-1]
        assert call["temperature"] == 0.2  # Low temp for consistency
        assert call["max_tokens"] == 1024


class TestJudgeIntegration:
    """Integration tests for Judge with various scenarios."""

    def test_evaluate_multiple_responses(self, mock_llm):
        """Test evaluating multiple responses in sequence."""
        judge = LegacyJudge(mock_llm)

        responses = [
            ('{"overall_score": 5, "strengths": [], "weaknesses": [], "scores": {}}', 5),
            ('{"overall_score": 3, "strengths": [], "weaknesses": [], "scores": {}}', 3),
            ('{"overall_score": 1, "strengths": [], "weaknesses": [], "scores": {}}', 1),
        ]

        for mock_response, expected_score in responses:
            mock_llm.queue_response(mock_response)

        for _, expected_score in responses:
            result = judge.evaluate("Test", "Test response")
            assert result.overall_score == expected_score

    def test_judge_preserves_raw_response(self, judge, mock_llm):
        """Test that raw LLM response is preserved."""
        raw = '{"overall_score": 4, "strengths": [], "weaknesses": [], "scores": {}, "reasoning": "test"}'
        mock_llm.queue_response(raw)

        result = judge.evaluate("Test", "Test")

        assert result.raw_response == raw


if __name__ == "__main__":
    pytest.main([__file__, "-v"])



# =============================================================================
# Tests for New Judge Implementation (evaluate_single / evaluate_pairwise)
# =============================================================================

from unittest.mock import patch
from agents.judge import JudgeError, Judge as NewJudge


class TestNewJudgeEvaluateSingle:
    """Tests for Judge.evaluate_single method."""

    def test_evaluate_single_returns_correct_structure(self):
        mock_response = '{"overall_score": 8.0, "subscores": {"correctness": 3, "completeness": 2, "clarity_and_style": 2, "safety": 1}, "tags": ["good"], "rationale": "Well-written response."}'
        with patch("llm.client.chat", return_value=mock_response):
            judge = NewJudge()
            result = judge.evaluate_single(task_description="Test", user_input="What is Python?", candidate_output="A language.")
        assert "overall_score" in result
        assert "subscores" in result
        assert result["overall_score"] == 8.0

    def test_evaluate_single_validates_subscores(self):
        mock_response = '{"overall_score": 5.0, "subscores": {"correctness": 2}, "tags": [], "rationale": "Test"}'
        with patch("llm.client.chat", return_value=mock_response):
            judge = NewJudge()
            with pytest.raises(JudgeError) as exc_info:
                judge.evaluate_single(task_description="Test", user_input="Test", candidate_output="Test")
            assert "Missing subscore" in str(exc_info.value)


class TestNewJudgeEvaluatePairwise:
    """Tests for Judge.evaluate_pairwise method."""

    def test_evaluate_pairwise_returns_correct_structure(self):
        mock_response = '{"winner": "B", "margin": "moderately", "tags": ["good"], "rationale": "B is better."}'
        with patch("llm.client.chat", return_value=mock_response):
            judge = NewJudge()
            result = judge.evaluate_pairwise(task_description="Test", user_input="Q?", output_a="A1", output_b="A2")
        assert result["winner"] == "B"
        assert result["margin"] == "moderately"

    def test_evaluate_pairwise_validates_winner(self):
        mock_response = '{"winner": "C", "margin": "slightly", "tags": [], "rationale": "Invalid"}'
        with patch("llm.client.chat", return_value=mock_response):
            judge = NewJudge()
            with pytest.raises(JudgeError) as exc_info:
                judge.evaluate_pairwise(task_description="Test", user_input="Q", output_a="A", output_b="B")
            assert "Invalid winner" in str(exc_info.value)

    def test_evaluate_pairwise_validates_margin(self):
        mock_response = '{"winner": "A", "margin": "hugely", "tags": [], "rationale": "Invalid"}'
        with patch("llm.client.chat", return_value=mock_response):
            judge = NewJudge()
            with pytest.raises(JudgeError) as exc_info:
                judge.evaluate_pairwise(task_description="Test", user_input="Q", output_a="A", output_b="B")
            assert "Invalid margin" in str(exc_info.value)


class TestNewJudgeErrorHandling:
    """Tests for Judge error handling."""

    def test_malformed_json_raises_judge_error(self):
        with patch("llm.client.chat", return_value="Not valid JSON"):
            judge = NewJudge()
            with pytest.raises(JudgeError) as exc_info:
                judge.evaluate_single(task_description="Test", user_input="Test", candidate_output="Test")
            assert "No JSON found" in str(exc_info.value)

    def test_missing_required_key_raises_judge_error(self):
        mock_response = '{"overall_score": 5.0, "subscores": {"correctness": 4, "completeness": 3, "clarity_and_style": 2, "safety": 1}}'
        with patch("llm.client.chat", return_value=mock_response):
            judge = NewJudge()
            with pytest.raises(JudgeError) as exc_info:
                judge.evaluate_single(task_description="Test", user_input="Test", candidate_output="Test")
            assert "Missing required key" in str(exc_info.value)
