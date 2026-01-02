"""Tests for agent-specific scoring rubric."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.agent_optimizer import (
    AgentConfig,
    AgentScorer,
    score_role_specificity,
    score_goal_clarity,
    score_termination_criteria,
    score_boundaries,
    score_tool_guidance,
    score_handoff_clarity,
)


class TestRoleSpecificityScoring:
    """Tests for role specificity scoring (0-20 points)."""

    def test_vague_role_scores_low(self):
        """Generic roles like 'Researcher' should score low."""
        score = score_role_specificity("Researcher")
        assert score <= 8

    def test_slightly_specific_role(self):
        """Slightly specific roles score medium."""
        score = score_role_specificity("Market Research Analyst")
        assert 8 < score <= 14

    def test_highly_specific_role_scores_high(self):
        """Highly specific roles with domain expertise score high."""
        score = score_role_specificity(
            "Senior Competitive Intelligence Analyst specializing in B2B SaaS markets"
        )
        assert score >= 15

    def test_empty_role_scores_zero(self):
        """Empty role should score 0."""
        score = score_role_specificity("")
        assert score == 0

    def test_role_with_experience_level(self):
        """Roles mentioning experience level get bonus points."""
        basic = score_role_specificity("Developer")
        senior = score_role_specificity("Senior Developer with 10 years experience")
        assert senior > basic


class TestGoalClarityScoring:
    """Tests for goal clarity scoring (0-25 points)."""

    def test_vague_goal_scores_low(self):
        """Vague goals like 'help with research' score low."""
        score = score_goal_clarity("Help with research tasks")
        assert score <= 10

    def test_goal_with_deliverables_scores_higher(self):
        """Goals with specific deliverables score higher."""
        score = score_goal_clarity("Find 5-7 key facts about the topic")
        assert score >= 15

    def test_goal_with_output_format_scores_higher(self):
        """Goals specifying output format score higher."""
        score = score_goal_clarity(
            "Analyze the data and produce a report with: executive summary, "
            "key findings (3-5 bullets), and recommendations"
        )
        assert score >= 18

    def test_quantified_goal_scores_well(self):
        """Goals with numbers/quantities score well."""
        vague = score_goal_clarity("Research competitors")
        specific = score_goal_clarity("Identify top 3 competitors with pricing data")
        assert specific > vague


class TestTerminationCriteriaScoring:
    """Tests for termination criteria scoring (0-15 points)."""

    def test_no_termination_scores_zero(self):
        """Goals without stop conditions score 0."""
        score = score_termination_criteria("Research the topic thoroughly")
        assert score == 0

    def test_explicit_stop_keyword(self):
        """Goals with 'STOP when' score high."""
        score = score_termination_criteria(
            "Find papers. STOP when you have 5 high-relevance papers."
        )
        assert score >= 12

    def test_completion_condition(self):
        """Goals with completion conditions score well."""
        score = score_termination_criteria(
            "Search databases until you find 3 matching results or exhaust all sources."
        )
        assert score >= 8

    def test_max_iterations_mentioned(self):
        """Goals mentioning max attempts/iterations score well."""
        score = score_termination_criteria(
            "Try up to 3 different search queries. Return best results found."
        )
        assert score >= 8


class TestBoundariesScoring:
    """Tests for boundaries/constraints scoring (0-20 points)."""

    def test_no_boundaries_scores_low(self):
        """Configs without constraints score low."""
        config = AgentConfig(
            framework="crewai",
            role="Helper",
            goal="Help the user",
            backstory="You are helpful."
        )
        score = score_boundaries(config)
        assert score <= 5

    def test_do_not_constraints(self):
        """Configs with 'DO NOT' constraints score higher."""
        config = AgentConfig(
            framework="crewai",
            role="Researcher",
            goal="Find facts. DO NOT make recommendations.",
            backstory="You focus only on facts."
        )
        score = score_boundaries(config)
        assert score >= 10

    def test_never_constraints(self):
        """Configs with 'NEVER' constraints score higher."""
        config = AgentConfig(
            framework="crewai",
            backstory="You NEVER speculate. You NEVER provide unverified information."
        )
        score = score_boundaries(config)
        assert score >= 12

    def test_explicit_role_boundaries(self):
        """Configs defining what's NOT the agent's job score higher."""
        config = AgentConfig(
            framework="crewai",
            backstory="Analysis is NOT your job - hand that off to the analyst agent."
        )
        score = score_boundaries(config)
        assert score >= 8

    def test_multiple_boundary_types(self):
        """Configs with multiple boundary types score highest."""
        config = AgentConfig(
            framework="crewai",
            goal="Find facts. DO NOT analyze.",
            backstory="You NEVER recommend. You ONLY report facts. "
                      "Strategy is NOT your responsibility."
        )
        score = score_boundaries(config)
        assert score >= 16


class TestToolGuidanceScoring:
    """Tests for tool guidance scoring (0-15 points)."""

    def test_no_tools_no_penalty(self):
        """Configs without tools shouldn't be penalized for tool guidance."""
        config = AgentConfig(framework="crewai", tools=[])
        score = score_tool_guidance(config)
        assert score >= 10  # Neutral score

    def test_tools_without_guidance_scores_low(self):
        """Configs with tools but no usage guidance score low."""
        config = AgentConfig(
            framework="crewai",
            tools=["search_tool", "calculator", "web_browser"],
            goal="Help the user with tasks."
        )
        score = score_tool_guidance(config)
        assert score <= 5

    def test_tools_with_when_to_use(self):
        """Configs explaining when to use tools score higher."""
        config = AgentConfig(
            framework="crewai",
            tools=["search_tool", "calculator"],
            goal="Use search_tool for finding information. "
                 "Use calculator for numerical analysis."
        )
        score = score_tool_guidance(config)
        assert score >= 10


class TestHandoffClarityScoring:
    """Tests for handoff clarity scoring (0-10 points, multi-agent only)."""

    def test_single_agent_full_score(self):
        """Single-agent configs get full handoff score by default."""
        config = AgentConfig(
            framework="crewai",
            role="Solo Agent",
            is_multi_agent=False
        )
        score = score_handoff_clarity(config)
        assert score == 10

    def test_multi_agent_no_handoff_scores_low(self):
        """Multi-agent configs without handoff info score low."""
        config = AgentConfig(
            framework="crewai",
            role="Researcher",
            backstory="You research things.",
            is_multi_agent=True
        )
        score = score_handoff_clarity(config)
        assert score <= 3

    def test_multi_agent_with_handoff(self):
        """Multi-agent configs with clear handoff score higher."""
        config = AgentConfig(
            framework="crewai",
            role="Researcher",
            backstory="You hand off clean briefs to the Strategy Agent.",
            is_multi_agent=True
        )
        score = score_handoff_clarity(config)
        assert score >= 7


class TestAgentScorerIntegration:
    """Integration tests for the full AgentScorer."""

    def test_score_poor_agent(self):
        """Test scoring a poorly configured agent."""
        config = AgentConfig(
            framework="crewai",
            role="Researcher",
            goal="Help with research",
            backstory="You are helpful."
        )
        scorer = AgentScorer()
        result = scorer.score(config)

        assert result.total_score < 40
        assert len(result.issues) >= 3

    def test_score_good_agent(self):
        """Test scoring a well-configured agent."""
        config = AgentConfig(
            framework="crewai",
            role="Senior Competitive Intelligence Analyst specializing in B2B SaaS",
            goal="Find 5-7 key facts about {topic} covering market size, top 3 competitors, "
                 "and recent news. STOP when you have credible sources for each category. "
                 "DO NOT analyze or recommend.",
            backstory="You have 10 years at Gartner. You cite sources for every claim. "
                      "You NEVER speculate. You hand off clean briefs to the strategy team.",
            tools=["search_tool", "news_api"]
        )
        scorer = AgentScorer()
        result = scorer.score(config)

        assert result.total_score >= 75
        assert len(result.issues) <= 2

    def test_score_breakdown_structure(self):
        """Test that score breakdown has all expected categories."""
        config = AgentConfig(framework="crewai", role="Test")
        scorer = AgentScorer()
        result = scorer.score(config)

        assert "role_specificity" in result.breakdown
        assert "goal_clarity" in result.breakdown
        assert "termination_criteria" in result.breakdown
        assert "boundaries" in result.breakdown
        assert "tool_guidance" in result.breakdown
        assert "handoff_clarity" in result.breakdown


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
