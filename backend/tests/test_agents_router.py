"""Tests for the agents router endpoints."""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

import pytest

# Add paths for imports
backend_path = Path(__file__).parent.parent
project_root = backend_path.parent
sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(project_root))


class TestPlanEndpoint:
    """Tests for POST /api/v1/agents/plan"""

    def test_plan_returns_skill_selection(self, mock_llm_client):
        """Test that plan endpoint returns selected skills."""
        # Queue mock planner response
        mock_llm_client.queue_response('''{
            "reasoning": "User wants to debug code",
            "steps": [{"skill": "code_debugger", "input_mapping": {"input": "user_request"}}]
        }''')

        from agents import Planner
        from prompts import SkillRegistry

        registry = SkillRegistry()
        planner = Planner(mock_llm_client, registry)

        plan = planner.plan("Help me debug this code")

        assert plan.is_valid
        assert "code_debugger" in plan.skill_names
        assert plan.reasoning == "User wants to debug code"

    def test_plan_with_summarization_request(self, mock_llm_client):
        """Test plan for summarization request."""
        mock_llm_client.queue_response('''{
            "reasoning": "User wants to summarize a document",
            "steps": [{"skill": "summarize_long_doc"}]
        }''')

        from agents import Planner
        from prompts import SkillRegistry

        registry = SkillRegistry()
        planner = Planner(mock_llm_client, registry)

        plan = planner.plan("Summarize this article")

        assert "summarize_long_doc" in plan.skill_names

    def test_plan_fallback_on_unknown_request(self, mock_llm_client):
        """Test that unknown requests fall back to general_assistant."""
        mock_llm_client.queue_response('''{
            "reasoning": "General question",
            "steps": [{"skill": "general_assistant"}]
        }''')

        from agents import Planner
        from prompts import SkillRegistry

        registry = SkillRegistry()
        planner = Planner(mock_llm_client, registry)

        plan = planner.plan("What is the meaning of life?")

        assert "general_assistant" in plan.skill_names

    def test_plan_validation_rejects_invalid_skills(self, mock_llm_client):
        """Test that invalid skills are rejected."""
        mock_llm_client.queue_response('''{
            "reasoning": "Test",
            "steps": [{"skill": "nonexistent_skill"}]
        }''')

        from agents import Planner
        from prompts import SkillRegistry

        registry = SkillRegistry()
        planner = Planner(mock_llm_client, registry)

        plan = planner.plan("Test")
        is_valid, errors = planner.validate_plan(plan)

        assert not is_valid
        assert len(errors) > 0


class TestExecuteEndpoint:
    """Tests for POST /api/v1/agents/execute"""

    def test_execute_renders_skill_prompt(self, mock_llm_client):
        """Test that execute renders the skill prompt correctly."""
        from prompts import SkillRegistry

        registry = SkillRegistry()
        skill = registry.get("code_debugger")

        prompt = skill.render(input="def foo(): pass", language="python")

        assert "def foo(): pass" in prompt
        assert "python" in prompt.lower()

    def test_execute_returns_llm_response(self, mock_llm_client):
        """Test that execute returns the LLM response."""
        mock_llm_client.queue_response("Here is the analysis of your code...")

        from prompts import SkillRegistry

        registry = SkillRegistry()
        skill = registry.get("code_debugger")
        prompt = skill.render(input="def foo(): pass")

        response = mock_llm_client.complete(
            prompt,
            model=skill.model,
            max_tokens=skill.max_tokens,
            temperature=skill.temperature,
        )

        assert response.content == "Here is the analysis of your code..."
        assert response.model == skill.model

    def test_execute_with_different_skills(self, mock_llm_client):
        """Test executing different skills."""
        from prompts import SkillRegistry

        registry = SkillRegistry()

        # Test summarizer
        summarizer = registry.get("summarize_long_doc")
        prompt = summarizer.render(input="Long document text here...")
        assert "Long document text here..." in prompt

        # Test general assistant
        assistant = registry.get("general_assistant")
        prompt = assistant.render(input="What is Python?")
        assert "What is Python?" in prompt


class TestEvaluateEndpoint:
    """Tests for POST /api/v1/agents/evaluate"""

    def test_evaluate_returns_judgment(self, mock_llm_client):
        """Test that evaluate returns a judgment."""
        mock_llm_client.queue_response('''{
            "scores": {"accuracy": 5, "clarity": 4},
            "overall_score": 4,
            "strengths": ["Clear explanation"],
            "weaknesses": ["Could be more detailed"],
            "reasoning": "Good response overall"
        }''')

        from agents import Judge

        judge = Judge(mock_llm_client)
        judgment = judge.evaluate(
            "What is Python?",
            "Python is a programming language."
        )

        assert judgment.overall_score == 4
        assert judgment.passed
        assert len(judgment.strengths) > 0

    def test_evaluate_with_custom_rubric(self, mock_llm_client):
        """Test evaluation with custom rubric."""
        mock_llm_client.queue_response('''{
            "scores": {"technical_accuracy": 5},
            "overall_score": 5,
            "strengths": ["Technically correct"],
            "weaknesses": [],
            "reasoning": "Excellent technical response"
        }''')

        from agents import Judge

        custom_rubric = "- Technical Accuracy: Is the answer technically correct?"
        judge = Judge(mock_llm_client, rubric=custom_rubric)

        judgment = judge.evaluate("Explain recursion", "Recursion is...")

        assert judgment.overall_score == 5
        # Verify custom rubric was used
        call = mock_llm_client.call_history[-1]
        assert "Technical Accuracy" in call["prompt"]

    def test_evaluate_failing_response(self, mock_llm_client):
        """Test evaluation of a poor response."""
        mock_llm_client.queue_response('''{
            "scores": {"accuracy": 1, "clarity": 2},
            "overall_score": 2,
            "strengths": [],
            "weaknesses": ["Incorrect", "Unclear"],
            "reasoning": "Poor response"
        }''')

        from agents import Judge

        judge = Judge(mock_llm_client)
        judgment = judge.evaluate("What is 2+2?", "The answer is 5")

        assert judgment.overall_score == 2
        assert not judgment.passed
        assert len(judgment.weaknesses) > 0


class TestCompareEndpoint:
    """Tests for POST /api/v1/agents/compare"""

    def test_compare_returns_winner(self, mock_llm_client):
        """Test that compare returns a winner."""
        mock_llm_client.queue_response('''{
            "winner": "B",
            "confidence": "high",
            "comparison": {
                "clarity": {"winner": "B", "explanation": "More clear"}
            },
            "reasoning": "B is more comprehensive"
        }''')

        from agents import Judge

        judge = Judge(mock_llm_client)
        result = judge.compare(
            "What is Python?",
            "A language.",
            "Python is a high-level programming language."
        )

        assert result.winner == "B"
        assert result.confidence == "high"

    def test_compare_tie_result(self, mock_llm_client):
        """Test comparison resulting in tie."""
        mock_llm_client.queue_response('''{
            "winner": "tie",
            "confidence": "medium",
            "comparison": {},
            "reasoning": "Both responses are equally good"
        }''')

        from agents import Judge

        judge = Judge(mock_llm_client)
        result = judge.compare("Test", "Response 1", "Response 2")

        assert result.winner == "tie"


class TestSkillsEndpoint:
    """Tests for GET /api/v1/agents/skills"""

    def test_list_skills_returns_all(self):
        """Test that listing skills returns all available skills."""
        from prompts import SkillRegistry

        registry = SkillRegistry()
        skills = registry.get_all()

        assert len(skills) >= 3
        skill_names = [s.name for s in skills]
        assert "code_debugger" in skill_names
        assert "summarize_long_doc" in skill_names
        assert "general_assistant" in skill_names

    def test_get_skill_by_name(self):
        """Test getting a specific skill."""
        from prompts import SkillRegistry

        registry = SkillRegistry()
        skill = registry.get("code_debugger")

        assert skill is not None
        assert skill.name == "code_debugger"
        assert "debugging" in skill.tags

    def test_get_skills_by_tag(self):
        """Test filtering skills by tag."""
        from prompts import SkillRegistry

        registry = SkillRegistry()
        code_skills = registry.get_by_tag("code")

        assert len(code_skills) >= 1
        assert all("code" in s.tags for s in code_skills)

    def test_skill_catalog_format(self):
        """Test that skill catalog is properly formatted."""
        from prompts import SkillRegistry

        registry = SkillRegistry()
        catalog = registry.get_catalog()

        assert "code_debugger" in catalog
        assert "summarize_long_doc" in catalog
        assert "Description:" in catalog


class TestAgentSchemas:
    """Tests for request/response schemas."""

    def test_plan_request_schema(self):
        """Test PlanRequest schema."""
        from app.schemas.agents import PlanRequest

        request = PlanRequest(user_request="Help me debug this code")
        assert request.user_request == "Help me debug this code"

    def test_plan_response_schema(self):
        """Test PlanResponse schema."""
        from app.schemas.agents import PlanResponse, PlanStepResponse

        step = PlanStepResponse(
            skill="code_debugger",
            input_mapping={"input": "user_request"},
            notes="Analyze code"
        )
        response = PlanResponse(
            reasoning="User wants to debug",
            steps=[step],
            is_valid=True
        )

        assert response.reasoning == "User wants to debug"
        assert len(response.steps) == 1
        assert response.steps[0].skill == "code_debugger"

    def test_execute_request_schema(self):
        """Test ExecuteRequest schema."""
        from app.schemas.agents import ExecuteRequest

        request = ExecuteRequest(
            skill="code_debugger",
            input="def foo(): pass",
            variables={"language": "python"}
        )

        assert request.skill == "code_debugger"
        assert request.input == "def foo(): pass"
        assert request.variables["language"] == "python"

    def test_evaluate_request_schema(self):
        """Test EvaluateRequest schema."""
        from app.schemas.agents import EvaluateRequest

        request = EvaluateRequest(
            request="What is Python?",
            response="Python is a language.",
            rubric="- Accuracy: Is it correct?"
        )

        assert request.request == "What is Python?"
        assert request.response == "Python is a language."

    def test_judgment_response_schema(self):
        """Test JudgmentResponse schema."""
        from app.schemas.agents import JudgmentResponse

        response = JudgmentResponse(
            scores={"accuracy": 5},
            overall_score=5,
            passed=True,
            strengths=["Clear"],
            weaknesses=[],
            reasoning="Good"
        )

        assert response.overall_score == 5
        assert response.passed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
