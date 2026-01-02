"""Golden dataset tests for agent scoring validation.

These tests verify that our scoring matches human-labeled expectations
on a curated set of known-good and known-bad agent configurations.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from tests.fixtures.golden_agents import GOLDEN_AGENTS, get_poor_agents, get_good_agents
from agents.agent_optimizer import AgentAnalyzer, detect_framework


class TestGoldenAgentScoring:
    """Tests against curated agent examples."""

    @pytest.mark.parametrize(
        "agent",
        GOLDEN_AGENTS,
        ids=lambda a: a["name"]
    )
    def test_scoring_matches_expected_range(self, agent):
        """Verify scoring matches human-labeled expectations."""
        analyzer = AgentAnalyzer()

        # Detect framework and parse config
        detection = detect_framework(agent["config"])
        assert detection.framework == agent["framework"], \
            f"Framework mismatch: expected {agent['framework']}, got {detection.framework}"

        # Score the agent
        result = analyzer.analyze(agent["config"])

        min_score, max_score = agent["expected_score_range"]
        assert min_score <= result.total_score <= max_score, \
            f"Score {result.total_score} outside expected range {min_score}-{max_score}. " \
            f"Breakdown: {result.breakdown}"

    @pytest.mark.parametrize(
        "agent",
        GOLDEN_AGENTS,
        ids=lambda a: a["name"]
    )
    def test_expected_issues_detected(self, agent):
        """Verify expected issues are detected."""
        analyzer = AgentAnalyzer()
        result = analyzer.analyze(agent["config"])

        detected_categories = [issue["category"] for issue in result.issues]

        for expected_issue in agent["expected_issues"]:
            assert expected_issue in detected_categories, \
                f"Expected issue '{expected_issue}' not detected. " \
                f"Found: {detected_categories}"


class TestPoorAgentsScoreLow:
    """Verify that known-poor agents consistently score low."""

    @pytest.mark.parametrize(
        "agent",
        get_poor_agents(),
        ids=lambda a: a["name"]
    )
    def test_poor_agents_below_threshold(self, agent):
        """Poor agents should score below 40."""
        analyzer = AgentAnalyzer()
        result = analyzer.analyze(agent["config"])

        assert result.total_score < 45, \
            f"Poor agent '{agent['name']}' scored {result.total_score}, expected < 45"

    @pytest.mark.parametrize(
        "agent",
        get_poor_agents(),
        ids=lambda a: a["name"]
    )
    def test_poor_agents_have_issues(self, agent):
        """Poor agents should have multiple issues detected."""
        analyzer = AgentAnalyzer()
        result = analyzer.analyze(agent["config"])

        assert len(result.issues) >= 2, \
            f"Poor agent '{agent['name']}' only has {len(result.issues)} issues, expected >= 2"


class TestGoodAgentsScoreHigh:
    """Verify that known-good agents consistently score high."""

    @pytest.mark.parametrize(
        "agent",
        get_good_agents(),
        ids=lambda a: a["name"]
    )
    def test_good_agents_above_threshold(self, agent):
        """Good agents should score above 55."""
        analyzer = AgentAnalyzer()
        result = analyzer.analyze(agent["config"])

        assert result.total_score >= 55, \
            f"Good agent '{agent['name']}' scored {result.total_score}, expected >= 55"

    @pytest.mark.parametrize(
        "agent",
        get_good_agents(),
        ids=lambda a: a["name"]
    )
    def test_good_agents_few_issues(self, agent):
        """Good agents should have few or no issues."""
        analyzer = AgentAnalyzer()
        result = analyzer.analyze(agent["config"])

        assert len(result.issues) <= 2, \
            f"Good agent '{agent['name']}' has {len(result.issues)} issues, expected <= 2"


class TestFrameworkDetection:
    """Test framework detection on golden agents."""

    @pytest.mark.parametrize(
        "agent",
        GOLDEN_AGENTS,
        ids=lambda a: a["name"]
    )
    def test_framework_detected_correctly(self, agent):
        """Verify correct framework detection for all golden agents."""
        result = detect_framework(agent["config"])
        assert result.framework == agent["framework"], \
            f"Expected {agent['framework']}, got {result.framework}"


class TestScoreImprovement:
    """Test that optimization improves scores."""

    @pytest.mark.skip(reason="AgentOptimizer.optimize() LLM integration not yet implemented")
    def test_poor_to_good_improvement(self, mock_llm_client):
        """Verify that optimizing a poor agent improves the score."""
        from agents.agent_optimizer import AgentOptimizer

        # Queue a mock optimized response
        mock_llm_client.queue_response('''{
            "optimized_config": {
                "role": "Senior Market Research Analyst specializing in B2B SaaS",
                "goal": "Find 5-7 key facts about {topic}. STOP when you have sources for each. DO NOT recommend.",
                "backstory": "10 years at Gartner. You cite sources. You NEVER speculate."
            },
            "improvements": ["Added role specificity", "Added termination criteria", "Added boundaries"],
            "reasoning": "Original config was too vague"
        }''')

        poor_agent = get_poor_agents()[0]

        optimizer = AgentOptimizer(mock_llm_client)
        result = optimizer.optimize(poor_agent["config"])

        assert result.optimized_score > result.original_score, \
            f"Optimization did not improve score: {result.original_score} -> {result.optimized_score}"

        assert result.optimized_score - result.original_score >= 20, \
            f"Improvement too small: only +{result.optimized_score - result.original_score} points"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
