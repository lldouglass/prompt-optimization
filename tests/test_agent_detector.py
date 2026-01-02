"""Tests for agent framework detection and parsing."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.agent_optimizer import (
    detect_framework,
    parse_crewai_config,
    parse_autogen_config,
    parse_langgraph_config,
    AgentConfig,
)


class TestFrameworkDetection:
    """Tests for detecting agent framework from input."""

    def test_detect_crewai_yaml_format(self):
        """Test detection of CrewAI YAML configuration."""
        config = """
        role: "Research Analyst"
        goal: "Find information about the topic"
        backstory: "You are a skilled researcher."
        tools:
          - search_tool
          - web_scraper
        """
        result = detect_framework(config)
        assert result.framework == "crewai"

    def test_detect_crewai_agent_constructor(self):
        """Test detection of CrewAI Agent() constructor."""
        config = """
        Agent(
            role="Data Analyst",
            goal="Analyze datasets",
            backstory="You have 10 years experience.",
            tools=[search_tool, calculator]
        )
        """
        result = detect_framework(config)
        assert result.framework == "crewai"

    def test_detect_autogen_assistant_agent(self):
        """Test detection of AutoGen AssistantAgent."""
        config = """
        AssistantAgent(
            name="analyst",
            system_message="You analyze data and provide insights.",
            description="For the group manager to route analysis tasks."
        )
        """
        result = detect_framework(config)
        assert result.framework == "autogen"

    def test_detect_autogen_conversable_agent(self):
        """Test detection of AutoGen ConversableAgent."""
        config = """
        ConversableAgent(
            name="coder",
            system_message="You write Python code.",
            llm_config={"model": "gpt-4"}
        )
        """
        result = detect_framework(config)
        assert result.framework == "autogen"

    def test_detect_langgraph_create_agent(self):
        """Test detection of LangGraph create_agent pattern."""
        config = """
        create_agent(
            model,
            tools=[search, calculator],
            system_prompt="You are a helpful research assistant."
        )
        """
        result = detect_framework(config)
        assert result.framework == "langgraph"

    def test_detect_langgraph_system_message(self):
        """Test detection of LangGraph SystemMessage pattern."""
        config = """
        SystemMessage(content="You are an expert analyst...")
        """
        result = detect_framework(config)
        assert result.framework == "langgraph"

    def test_detect_generic_system_prompt(self):
        """Test detection of plain system prompt."""
        config = "You are a helpful assistant that answers questions about programming."
        result = detect_framework(config)
        assert result.framework == "generic"

    def test_detect_empty_input(self):
        """Test handling of empty input."""
        result = detect_framework("")
        assert result.framework == "generic"
        assert result.confidence == "low"


class TestCrewAIParsing:
    """Tests for parsing CrewAI configurations."""

    def test_parse_basic_config(self):
        """Test parsing a basic CrewAI config."""
        config = """
        role: "Researcher"
        goal: "Find information"
        backstory: "You are helpful."
        """
        result = parse_crewai_config(config)

        assert result.role == "Researcher"
        assert result.goal == "Find information"
        assert result.backstory == "You are helpful."

    def test_parse_with_tools(self):
        """Test parsing config with tools list."""
        config = """
        role: "Analyst"
        goal: "Analyze data"
        backstory: "Expert analyst."
        tools:
          - search_tool
          - calculator
          - web_browser
        """
        result = parse_crewai_config(config)

        assert len(result.tools) == 3
        assert "search_tool" in result.tools

    def test_parse_multiline_goal(self):
        """Test parsing multiline goal with YAML literal block."""
        config = """
        role: "Writer"
        goal: |
          Write compelling content that:
          - Engages the reader
          - Provides value
          - Is well-structured
        backstory: "Professional writer."
        """
        result = parse_crewai_config(config)

        assert "Engages the reader" in result.goal
        assert "Provides value" in result.goal

    def test_parse_python_constructor(self):
        """Test parsing Python Agent() constructor syntax."""
        config = '''
        Agent(
            role="Senior Developer",
            goal="Write clean, maintainable code",
            backstory="20 years of experience in software development."
        )
        '''
        result = parse_crewai_config(config)

        assert result.role == "Senior Developer"
        assert "clean" in result.goal.lower()


class TestAutoGenParsing:
    """Tests for parsing AutoGen configurations."""

    def test_parse_assistant_agent(self):
        """Test parsing AutoGen AssistantAgent."""
        config = """
        AssistantAgent(
            name="researcher",
            system_message="You are a research assistant that finds information.",
            description="Routes research queries to this agent."
        )
        """
        result = parse_autogen_config(config)

        assert result.name == "researcher"
        assert "research assistant" in result.system_message.lower()
        assert result.description is not None

    def test_parse_without_description(self):
        """Test parsing AutoGen config without description."""
        config = """
        AssistantAgent(
            name="coder",
            system_message="You write Python code."
        )
        """
        result = parse_autogen_config(config)

        assert result.name == "coder"
        assert result.description is None or result.description == ""


class TestLangGraphParsing:
    """Tests for parsing LangGraph configurations."""

    def test_parse_create_agent(self):
        """Test parsing LangGraph create_agent call."""
        config = """
        create_agent(
            model,
            tools=[search, calculator],
            system_prompt="You are an expert data analyst who helps users understand their data."
        )
        """
        result = parse_langgraph_config(config)

        assert "data analyst" in result.system_prompt.lower()
        assert len(result.tools) >= 1

    def test_parse_system_message(self):
        """Test parsing LangGraph SystemMessage."""
        config = """
        SystemMessage(content="You are a helpful coding assistant. You write clean Python code.")
        """
        result = parse_langgraph_config(config)

        assert "coding assistant" in result.system_prompt.lower()


class TestAgentConfigDataclass:
    """Tests for the AgentConfig dataclass."""

    def test_create_config(self):
        """Test creating an AgentConfig."""
        config = AgentConfig(
            framework="crewai",
            role="Researcher",
            goal="Find information",
            backstory="You are helpful.",
        )

        assert config.framework == "crewai"
        assert config.role == "Researcher"

    def test_default_values(self):
        """Test default values in AgentConfig."""
        config = AgentConfig(framework="generic")

        assert config.role == ""
        assert config.goal == ""
        assert config.tools == []
        assert config.constraints == []

    def test_has_termination_criteria(self):
        """Test detection of termination criteria in goal."""
        config_with = AgentConfig(
            framework="crewai",
            goal="Find 5 papers. STOP when you have 5 papers."
        )
        config_without = AgentConfig(
            framework="crewai",
            goal="Research the topic thoroughly."
        )

        assert config_with.has_termination_criteria() is True
        assert config_without.has_termination_criteria() is False

    def test_has_boundaries(self):
        """Test detection of explicit boundaries."""
        config_with = AgentConfig(
            framework="crewai",
            backstory="You NEVER make recommendations. DO NOT speculate."
        )
        config_without = AgentConfig(
            framework="crewai",
            backstory="You are a helpful assistant."
        )

        assert config_with.has_explicit_boundaries() is True
        assert config_without.has_explicit_boundaries() is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
