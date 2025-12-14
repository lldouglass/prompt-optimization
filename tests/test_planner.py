"""Tests for the Planner agent."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents import Planner, Plan, PlanStep
from llm import MockLLMClient
from prompts import SkillRegistry


@pytest.fixture
def mock_llm():
    """Create a mock LLM client."""
    return MockLLMClient()


@pytest.fixture
def registry():
    """Create a skill registry."""
    return SkillRegistry()


@pytest.fixture
def planner(mock_llm, registry):
    """Create a planner with mock LLM."""
    return Planner(mock_llm, registry)


class TestPlanStep:
    """Tests for PlanStep dataclass."""

    def test_create_step(self):
        step = PlanStep(
            skill="summarize_long_doc",
            input_mapping={"input": "user_request"},
            notes="Test note",
        )
        assert step.skill == "summarize_long_doc"
        assert step.input_mapping == {"input": "user_request"}
        assert step.notes == "Test note"

    def test_default_values(self):
        step = PlanStep(skill="test")
        assert step.input_mapping == {}
        assert step.notes == ""


class TestPlan:
    """Tests for Plan dataclass."""

    def test_is_valid_with_steps(self):
        plan = Plan(
            reasoning="Test reasoning",
            steps=[PlanStep(skill="test")],
        )
        assert plan.is_valid is True

    def test_is_valid_without_steps(self):
        plan = Plan(reasoning="Test", steps=[])
        assert plan.is_valid is False

    def test_skill_names(self):
        plan = Plan(
            reasoning="Test",
            steps=[
                PlanStep(skill="skill1"),
                PlanStep(skill="skill2"),
            ],
        )
        assert plan.skill_names == ["skill1", "skill2"]


class TestPlanner:
    """Tests for the Planner agent."""

    def test_plan_selects_code_debugger(self, planner, mock_llm):
        """Test that planner selects code_debugger for code-related requests."""
        mock_llm.queue_response('''{
            "reasoning": "User wants to debug code",
            "steps": [
                {
                    "skill": "code_debugger",
                    "input_mapping": {"input": "user_request"}
                }
            ]
        }''')

        plan = planner.plan("Help me fix this Python bug")

        assert plan.is_valid
        assert "code_debugger" in plan.skill_names
        assert "debug" in plan.reasoning.lower()

    def test_plan_selects_summarizer(self, planner, mock_llm):
        """Test that planner selects summarizer for document requests."""
        mock_llm.queue_response('''{
            "reasoning": "User wants to summarize a document",
            "steps": [
                {
                    "skill": "summarize_long_doc",
                    "input_mapping": {"input": "user_request"}
                }
            ]
        }''')

        plan = planner.plan("Summarize this article for me")

        assert plan.is_valid
        assert "summarize_long_doc" in plan.skill_names

    def test_plan_fallback_on_invalid_json(self, planner, mock_llm):
        """Test fallback behavior when LLM returns invalid JSON."""
        mock_llm.queue_response("This is not valid JSON at all")

        plan = planner.plan("Random request")

        assert plan.is_valid
        assert "general_assistant" in plan.skill_names
        assert "fallback" in plan.reasoning.lower()

    def test_plan_multi_step(self, planner, mock_llm):
        """Test that planner can create multi-step plans."""
        mock_llm.queue_response('''{
            "reasoning": "Complex request needs multiple skills",
            "steps": [
                {"skill": "summarize_long_doc"},
                {"skill": "code_debugger"}
            ]
        }''')

        plan = planner.plan("Summarize this document and also check the code")

        assert len(plan.steps) == 2
        assert plan.skill_names == ["summarize_long_doc", "code_debugger"]

    def test_validate_plan_valid(self, planner, mock_llm):
        """Test plan validation with valid skills."""
        mock_llm.queue_response('''{
            "reasoning": "Test",
            "steps": [{"skill": "code_debugger"}]
        }''')

        plan = planner.plan("Test")
        is_valid, errors = planner.validate_plan(plan)

        assert is_valid
        assert errors == []

    def test_validate_plan_invalid_skill(self, planner, mock_llm):
        """Test plan validation with invalid skills."""
        mock_llm.queue_response('''{
            "reasoning": "Test",
            "steps": [{"skill": "nonexistent_skill"}]
        }''')

        plan = planner.plan("Test")
        is_valid, errors = planner.validate_plan(plan)

        assert not is_valid
        assert len(errors) == 1
        assert "nonexistent_skill" in errors[0]

    def test_llm_call_recorded(self, planner, mock_llm):
        """Test that LLM calls are properly recorded."""
        mock_llm.queue_response('''{
            "reasoning": "Test",
            "steps": [{"skill": "general_assistant"}]
        }''')

        planner.plan("Test request")

        assert len(mock_llm.call_history) == 1
        assert mock_llm.call_history[0]["method"] == "complete_chat"
        assert "Test request" in mock_llm.call_history[0]["messages"][1]["content"]


class TestSkillRegistry:
    """Tests for SkillRegistry (used by planner)."""

    def test_load_skills(self, registry):
        """Test that skills are loaded from YAML files."""
        registry.load()
        assert len(registry) >= 3  # At least our 3 example skills

    def test_get_skill(self, registry):
        """Test getting a skill by name."""
        skill = registry.get("code_debugger")
        assert skill is not None
        assert skill.name == "code_debugger"
        assert "debugging" in skill.tags

    def test_get_nonexistent_skill(self, registry):
        """Test getting a nonexistent skill returns None."""
        skill = registry.get("nonexistent")
        assert skill is None

    def test_contains(self, registry):
        """Test skill existence check."""
        assert "code_debugger" in registry
        assert "nonexistent" not in registry

    def test_get_by_tag(self, registry):
        """Test getting skills by tag."""
        code_skills = registry.get_by_tag("code")
        assert len(code_skills) >= 1
        assert all("code" in s.tags for s in code_skills)

    def test_get_catalog(self, registry):
        """Test catalog generation."""
        catalog = registry.get_catalog()
        assert "code_debugger" in catalog
        assert "summarize_long_doc" in catalog
        assert "general_assistant" in catalog

    def test_skill_render(self, registry):
        """Test skill prompt rendering."""
        skill = registry.get("general_assistant")
        prompt = skill.render(input="Test input")
        assert "Test input" in prompt
        assert "{{input}}" not in prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
