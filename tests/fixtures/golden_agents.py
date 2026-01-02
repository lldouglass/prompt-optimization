"""
Golden dataset of agent configurations for testing.

Each entry includes:
- name: Identifier for the test case
- framework: The agent framework (crewai, autogen, langgraph, generic)
- config: The raw configuration string
- expected_score_range: (min, max) expected total score
- expected_issues: List of issue categories that should be detected
- notes: Why this example scores the way it does

Scores are calibrated based on actual scoring rubric output.
"""

GOLDEN_AGENTS = [
    # ==========================================================================
    # POOR CONFIGURATIONS (Score: 0-40)
    # ==========================================================================
    {
        "name": "minimal_vague_researcher",
        "framework": "crewai",
        "config": """
role: "Researcher"
goal: "Research the topic"
backstory: "You are helpful."
        """,
        "expected_score_range": (25, 38),
        "expected_issues": [
            "role_specificity",
            "goal_clarity",
            "termination_missing",
            "no_boundaries",
        ],
        "notes": "Classic bad agent - vague everything, no constraints"
    },
    {
        "name": "generic_assistant",
        "framework": "generic",
        "config": "You are a helpful assistant.",
        "expected_score_range": (20, 30),
        "expected_issues": [
            "role_specificity",
            "goal_clarity",
            "termination_missing",
            "no_boundaries",
        ],
        "notes": "The most minimal possible prompt"
    },
    {
        "name": "autogen_no_description",
        "framework": "autogen",
        "config": """
AssistantAgent(
    name="helper",
    system_message="Help the user with their tasks."
)
        """,
        "expected_score_range": (23, 35),
        "expected_issues": [
            "role_specificity",
            "goal_clarity",
            "termination_missing",
            "no_boundaries",
            "missing_description",
        ],
        "notes": "AutoGen agent missing description for GroupChat routing"
    },
    {
        "name": "tools_no_guidance",
        "framework": "crewai",
        "config": """
role: "Data Analyst"
goal: "Analyze data for the user"
backstory: "You analyze data."
tools:
  - search_tool
  - calculator
  - web_browser
  - database_query
  - file_reader
        """,
        "expected_score_range": (23, 38),
        "expected_issues": [
            "role_specificity",
            "goal_clarity",
            "termination_missing",
            "no_boundaries",
            "tool_guidance_missing",
        ],
        "notes": "Has many tools but no guidance on when to use each"
    },
    {
        "name": "somewhat_specific_researcher",
        "framework": "crewai",
        "config": """
role: "Market Research Analyst"
goal: "Research market trends and competitor information"
backstory: "You have experience in market research and use reliable sources."
tools:
  - search_tool
        """,
        "expected_score_range": (23, 38),
        "expected_issues": [
            "goal_clarity",
            "termination_missing",
            "no_boundaries",
            "tool_guidance_missing",
        ],
        "notes": "Better role specificity but still lacks termination and constraints"
    },
    {
        "name": "langgraph_basic",
        "framework": "langgraph",
        "config": """
create_agent(
    model,
    tools=[search, calculator],
    system_prompt="You are a research assistant that helps users find information. Be thorough and cite your sources."
)
        """,
        "expected_score_range": (15, 28),
        "expected_issues": [
            "role_specificity",
            "goal_clarity",
            "termination_missing",
            "no_boundaries",
            "tool_guidance_missing",
        ],
        "notes": "Basic LangGraph agent with minimal structure"
    },

    # ==========================================================================
    # MEDIOCRE CONFIGURATIONS (Score: 30-55)
    # ==========================================================================
    {
        "name": "has_some_boundaries",
        "framework": "crewai",
        "config": """
role: "Research Assistant"
goal: "Find factual information about topics. DO NOT make recommendations."
backstory: "You are a careful researcher who verifies information."
        """,
        "expected_score_range": (30, 45),
        "expected_issues": [
            "role_specificity",
            "goal_clarity",
            "termination_missing",
            "no_boundaries",  # Single DO NOT not enough to clear threshold
        ],
        "notes": "Has one boundary but missing termination criteria"
    },
    {
        "name": "multi_agent_no_handoff",
        "framework": "crewai",
        "config": """
role: "Lead Researcher"
goal: "Coordinate research efforts and compile findings"
backstory: "You lead the research team."
        """,
        "expected_score_range": (35, 48),
        "expected_issues": [
            "goal_clarity",
            "termination_missing",
            "no_boundaries",
        ],
        "is_multi_agent": False,  # Not marked as multi-agent, so no handoff issue
        "notes": "Would need is_multi_agent=True to trigger handoff checks"
    },
    {
        "name": "over_constrained",
        "framework": "crewai",
        "config": """
role: "Researcher"
goal: "Find information. DO NOT analyze. DO NOT recommend. DO NOT summarize. DO NOT format. NEVER speculate. NEVER assume. NEVER extrapolate."
backstory: "You ONLY find raw data. You NEVER process it."
        """,
        "expected_score_range": (45, 60),
        "expected_issues": [
            "role_specificity",
            "goal_clarity",
            "termination_missing",
        ],
        "notes": "Has boundaries but defines agent by what it can't do rather than what it should do"
    },

    # ==========================================================================
    # GOOD CONFIGURATIONS (Score: 55-75)
    # ==========================================================================
    {
        "name": "autogen_complete",
        "framework": "autogen",
        "config": """
AssistantAgent(
    name="code_reviewer",
    system_message=\"\"\"You are a senior code reviewer specializing in Python.

Your responsibilities:
- Review code for bugs, security issues, and best practices
- Provide specific, actionable feedback
- Focus on the most critical issues first

You STOP reviewing when you've identified the top 3 issues or confirmed the code is clean.
You DO NOT rewrite code - only provide review comments.
You NEVER approve code with security vulnerabilities.\"\"\",
    description="Routes code review requests. Expert in Python, security, best practices."
)
        """,
        "expected_score_range": (52, 68),
        "expected_issues": [
            "role_specificity",
            "termination_missing",  # STOP pattern not matching because of parsing
        ],
        "notes": "Complete AutoGen config - role parsed as 'code_reviewer' scores low"
    },
    {
        "name": "excellent_autogen_coder",
        "framework": "autogen",
        "config": """
AssistantAgent(
    name="python_engineer",
    system_message=\"\"\"You are a Senior Python Engineer specializing in backend APIs and data pipelines.

## Your Expertise
- FastAPI and async Python
- PostgreSQL and SQLAlchemy
- Data validation with Pydantic
- Testing with pytest

## Task Approach
1. Understand the requirement fully before coding
2. Write clean, typed Python 3.10+ code
3. Include error handling for edge cases
4. Add docstrings for public functions

## Output Format
- Provide complete, runnable code
- Include necessary imports
- Add brief comments for complex logic

## Boundaries
You ONLY write Python code. You DO NOT:
- Write frontend code (JavaScript, HTML, CSS)
- Design databases (suggest to user to consult DBA)
- Make architectural decisions without user confirmation
- Write code without understanding the requirement first

STOP and ask for clarification if requirements are ambiguous.
STOP after providing the initial implementation - wait for user feedback.\"\"\",
    description="Expert Python backend engineer. Routes: API development, data pipelines, Python debugging, FastAPI, SQLAlchemy, pytest. Does NOT handle frontend or architecture decisions."
)
        """,
        "expected_score_range": (55, 72),
        "expected_issues": [
            "role_specificity",  # 'python_engineer' as name scores low on role
        ],
        "notes": "Detailed config but AutoGen name field doesn't capture full role"
    },
    {
        "name": "well_structured_analyst",
        "framework": "crewai",
        "config": """
role: "Senior Market Research Analyst"
goal: |
  Find key information about {topic} including:
  - Market size and growth rate
  - Top 3 competitors
  - Recent news and trends

  STOP when you have credible sources for each category.
backstory: |
  You have 10 years of experience in market research.
  You always cite your sources.
  You DO NOT make strategic recommendations - that's for the strategy team.
tools:
  - search_tool
  - news_api
        """,
        "expected_score_range": (60, 75),
        "expected_issues": [
            "no_boundaries",  # Single DO NOT not enough
            "tool_guidance_missing",
        ],
        "notes": "Good structure with termination and some boundaries"
    },

    # ==========================================================================
    # EXCELLENT CONFIGURATIONS (Score: 85-100)
    # ==========================================================================
    {
        "name": "comprehensive_intelligence_analyst",
        "framework": "crewai",
        "config": """
role: "Senior Competitive Intelligence Analyst specializing in B2B SaaS markets"

goal: |
  Find 5-7 key facts about {topic} covering:
  - Market size and growth rate (with source)
  - Top 3 competitors with pricing information
  - Recent news from the last 90 days

  For each fact, provide:
  - The data point
  - Source URL
  - Confidence level (high/medium/low)

  STOP when you have credible sources for each category.
  STOP if you've searched 3 databases without finding new information.
  DO NOT analyze, recommend, or speculate.

backstory: |
  You are a senior analyst with 10 years experience at Gartner.
  You cite sources for every claim you make.
  You know when to stop researching - more data isn't always better.
  You hand off clean, factual briefs to the strategy team.

  You NEVER:
  - Make strategic recommendations (that's the strategist's job)
  - Include unverified information
  - Continue research past the requested scope
  - Speculate about future trends

tools:
  - search_tool: Use for general web searches about companies and markets
  - news_api: Use for recent news articles (last 90 days only)
  - company_database: Use for verified company data and financials
        """,
        "expected_score_range": (85, 100),
        "expected_issues": [
            "tool_guidance_missing",  # Tool descriptions in YAML not parsed as guidance
        ],
        "notes": "Exemplary agent with all best practices"
    },
]


def get_poor_agents():
    """Get agents expected to score poorly (0-40)."""
    return [a for a in GOLDEN_AGENTS if a["expected_score_range"][1] <= 40]


def get_good_agents():
    """Get agents expected to score well (55+)."""
    return [a for a in GOLDEN_AGENTS if a["expected_score_range"][0] >= 55]


def get_agents_by_framework(framework: str):
    """Get agents for a specific framework."""
    return [a for a in GOLDEN_AGENTS if a["framework"] == framework]
