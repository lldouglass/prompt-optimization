"""
Agent Optimizer Module

Provides detection, parsing, scoring, and optimization of AI agent configurations
for popular frameworks: CrewAI, AutoGen, LangGraph, and generic system prompts.

This module implements the "Agent Mode" feature for PromptLab.
"""

import re
from dataclasses import dataclass, field
from typing import Any

import yaml


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class AgentConfig:
    """Parsed agent configuration."""

    framework: str  # crewai, autogen, langgraph, generic

    # Common fields
    role: str = ""
    goal: str = ""
    backstory: str = ""
    system_prompt: str = ""  # For LangGraph/generic

    # AutoGen-specific
    name: str = ""
    system_message: str = ""
    description: str = ""  # For GroupChat routing

    # Tools
    tools: list[str] = field(default_factory=list)
    tool_descriptions: dict[str, str] = field(default_factory=dict)

    # Constraints
    constraints: list[str] = field(default_factory=list)

    # Multi-agent context
    is_multi_agent: bool = False

    def has_termination_criteria(self) -> bool:
        """Check if the goal/prompt has explicit termination criteria."""
        text = f"{self.goal} {self.system_prompt} {self.system_message}".lower()
        termination_patterns = [
            r"\bstop\s+when\b",
            r"\bstop\s+if\b",
            r"\bstop\s+after\b",
            r"\buntil\s+you\s+have\b",
            r"\bmax(imum)?\s+\d+",
            r"\bup\s+to\s+\d+",
            r"\bno\s+more\s+than\s+\d+",
            r"\bfinish\s+when\b",
            r"\bcomplete\s+when\b",
        ]
        return any(re.search(pattern, text) for pattern in termination_patterns)

    def has_explicit_boundaries(self) -> bool:
        """Check if the config has explicit DO NOT / NEVER constraints."""
        text = f"{self.goal} {self.backstory} {self.system_prompt} {self.system_message}".lower()
        boundary_patterns = [
            r"\bdo\s+not\b",
            r"\bdon'?t\b",
            r"\bnever\b",
            r"\bonly\b",
            r"\bnot\s+your\s+(job|responsibility|role)\b",
            r"\bis\s+not\s+your\b",
        ]
        return any(re.search(pattern, text) for pattern in boundary_patterns)


@dataclass
class FrameworkDetection:
    """Result of framework detection."""

    framework: str  # crewai, autogen, langgraph, generic
    confidence: str  # high, medium, low
    matched_patterns: list[str] = field(default_factory=list)


@dataclass
class ScoringResult:
    """Result of scoring an agent configuration."""

    total_score: int  # 0-100
    breakdown: dict[str, int] = field(default_factory=dict)
    issues: list[dict[str, Any]] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


@dataclass
class AgentOptimizationResult:
    """Result of optimizing an agent configuration."""

    original_config: str
    optimized_config: str
    original_score: int
    optimized_score: int
    improvements: list[str] = field(default_factory=list)
    reasoning: str = ""


# =============================================================================
# Framework Detection
# =============================================================================

def detect_framework(config: str) -> FrameworkDetection:
    """
    Detect which agent framework a configuration is for.

    Args:
        config: Raw configuration string (YAML, Python, or plain text)

    Returns:
        FrameworkDetection with framework type and confidence
    """
    config_lower = config.lower().strip()
    matched = []

    # Check for CrewAI patterns (both YAML and Python constructor syntax)
    crewai_patterns = [
        (r"\brole\s*:", "role: field"),
        (r"\bgoal\s*:", "goal: field"),
        (r"\bbackstory\s*:", "backstory: field"),
        (r"\brole\s*=", "role= param"),
        (r"\bgoal\s*=", "goal= param"),
        (r"\bbackstory\s*=", "backstory= param"),
        (r"Agent\s*\(", "Agent() constructor"),
    ]
    crewai_matches = sum(1 for pattern, name in crewai_patterns if re.search(pattern, config))
    if crewai_matches >= 2:
        matched.append("crewai")

    # Check for AutoGen patterns
    autogen_patterns = [
        (r"AssistantAgent\s*\(", "AssistantAgent()"),
        (r"ConversableAgent\s*\(", "ConversableAgent()"),
        (r"UserProxyAgent\s*\(", "UserProxyAgent()"),
        (r"\bsystem_message\s*=", "system_message="),
        (r"\bdescription\s*=", "description="),
    ]
    autogen_matches = sum(1 for pattern, name in autogen_patterns if re.search(pattern, config))
    if autogen_matches >= 1:
        matched.append("autogen")

    # Check for LangGraph patterns
    langgraph_patterns = [
        (r"create_agent\s*\(", "create_agent()"),
        (r"SystemMessage\s*\(", "SystemMessage()"),
        (r"\bsystem_prompt\s*=", "system_prompt="),
    ]
    langgraph_matches = sum(1 for pattern, name in langgraph_patterns if re.search(pattern, config))
    if langgraph_matches >= 1:
        matched.append("langgraph")

    # Determine winner
    if "autogen" in matched:
        return FrameworkDetection("autogen", "high", matched)
    elif "langgraph" in matched:
        return FrameworkDetection("langgraph", "high", matched)
    elif "crewai" in matched:
        return FrameworkDetection("crewai", "high", matched)
    else:
        return FrameworkDetection("generic", "low" if not config.strip() else "medium", [])


# =============================================================================
# Config Parsing
# =============================================================================

def parse_crewai_config(config: str) -> AgentConfig:
    """Parse a CrewAI agent configuration."""
    result = AgentConfig(framework="crewai")

    # Try YAML parsing first
    try:
        parsed = yaml.safe_load(config)
        if isinstance(parsed, dict):
            result.role = parsed.get("role", "")
            result.goal = parsed.get("goal", "")
            result.backstory = parsed.get("backstory", "")
            tools = parsed.get("tools", [])
            result.tools = tools if isinstance(tools, list) else []
            return result
    except yaml.YAMLError:
        pass

    # Fallback to regex for Python constructor syntax
    role_match = re.search(r'role\s*=\s*["\']([^"\']+)["\']', config)
    goal_match = re.search(r'goal\s*=\s*["\']([^"\']+)["\']', config)
    backstory_match = re.search(r'backstory\s*=\s*["\']([^"\']+)["\']', config)

    if role_match:
        result.role = role_match.group(1)
    if goal_match:
        result.goal = goal_match.group(1)
    if backstory_match:
        result.backstory = backstory_match.group(1)

    return result


def parse_autogen_config(config: str) -> AgentConfig:
    """Parse an AutoGen agent configuration."""
    result = AgentConfig(framework="autogen")

    # Extract name
    name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', config)
    if name_match:
        result.name = name_match.group(1)

    # Extract system_message (may be multiline with triple quotes)
    sys_msg_match = re.search(
        r'system_message\s*=\s*(?:"""(.+?)"""|\'\'\'(.+?)\'\'\'|["\']([^"\']+)["\'])',
        config,
        re.DOTALL
    )
    if sys_msg_match:
        result.system_message = sys_msg_match.group(1) or sys_msg_match.group(2) or sys_msg_match.group(3) or ""

    # Extract description
    desc_match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', config)
    if desc_match:
        result.description = desc_match.group(1)

    return result


def parse_langgraph_config(config: str) -> AgentConfig:
    """Parse a LangGraph agent configuration."""
    result = AgentConfig(framework="langgraph")

    # Extract system_prompt
    prompt_match = re.search(
        r'system_prompt\s*=\s*["\']([^"\']+)["\']',
        config
    )
    if prompt_match:
        result.system_prompt = prompt_match.group(1)

    # Extract from SystemMessage
    sys_msg_match = re.search(
        r'SystemMessage\s*\(\s*content\s*=\s*["\']([^"\']+)["\']',
        config
    )
    if sys_msg_match:
        result.system_prompt = sys_msg_match.group(1)

    # Extract tools
    tools_match = re.search(r'tools\s*=\s*\[([^\]]+)\]', config)
    if tools_match:
        tools_str = tools_match.group(1)
        result.tools = [t.strip().strip("'\"") for t in tools_str.split(",") if t.strip()]

    return result


# =============================================================================
# Scoring Functions
# =============================================================================

def score_role_specificity(role: str) -> int:
    """
    Score role specificity (0-20 points).

    - 0-5: Generic (e.g., "Assistant", "Helper")
    - 6-8: Basic domain (e.g., "Researcher", "Developer")
    - 9-14: Specific domain (e.g., "Market Research Analyst")
    - 15-20: Expert level (e.g., "Senior Competitive Intelligence Analyst specializing in B2B SaaS")
    """
    if not role.strip():
        return 0

    role_lower = role.lower()
    word_count = len(role.split())

    # Very generic single-word terms
    generic_terms = ["assistant", "helper", "agent", "bot"]
    if any(term in role_lower for term in generic_terms) and word_count <= 2:
        return 3

    # Single-word domain terms are still vague
    domain_terms = ["analyst", "engineer", "developer", "researcher", "specialist", "expert", "writer"]
    is_domain_term = any(term in role_lower for term in domain_terms)

    if word_count == 1:
        # Single word role
        if is_domain_term:
            return 6  # Basic domain term alone
        return 4  # Unknown single word

    # Multi-word roles start with higher base
    score = 7

    # Bonus for domain specificity
    if is_domain_term:
        score += 2

    # Bonus for seniority/experience
    seniority_terms = ["senior", "lead", "principal", "expert", "years experience", "experienced"]
    if any(term in role_lower for term in seniority_terms):
        score += 4

    # Bonus for specialization
    if "specializing" in role_lower or "specialized" in role_lower or "focusing on" in role_lower:
        score += 4

    # Bonus for industry/niche
    industry_terms = ["saas", "b2b", "fintech", "healthcare", "enterprise", "startup"]
    if any(term in role_lower for term in industry_terms):
        score += 3

    # Length bonus (more descriptive = usually more specific)
    word_count = len(role.split())
    if word_count >= 5:
        score += 2
    elif word_count >= 3:
        score += 1

    return min(score, 20)


def score_goal_clarity(goal: str) -> int:
    """
    Score goal clarity (0-25 points).

    - Specific deliverables
    - Quantified outputs
    - Clear output format
    """
    if not goal.strip():
        return 0

    score = 5  # Base score for having any goal
    goal_lower = goal.lower()

    # Bonus for quantified deliverables (numbers indicate specificity)
    numbers_found = re.findall(r'\d+', goal)
    if numbers_found:
        score += 6
        # Extra bonus for ranges like "5-7" or "3-5"
        if re.search(r'\d+\s*[-–]\s*\d+', goal):
            score += 2

    # Bonus for specific output format
    format_indicators = [
        "for each", "provide:", "include:", "format:", "output:",
        "bullet", "list", "table", "summary", "report", "produce"
    ]
    format_matches = sum(1 for ind in format_indicators if ind in goal_lower)
    score += min(format_matches * 3, 6)

    # Bonus for structured requirements (multiple items)
    if re.search(r'[-•*]\s+\w', goal) or re.search(r'\d+\.\s+\w', goal):
        score += 4

    # Bonus for covering multiple aspects
    if goal.count("-") >= 2 or goal.count("•") >= 2 or goal.count(",") >= 2:
        score += 2

    # Bonus for action verbs indicating clear deliverables
    action_verbs = ["find", "identify", "analyze", "create", "generate", "extract", "compile"]
    if any(verb in goal_lower for verb in action_verbs):
        score += 2

    # Penalty for vague language
    vague_terms = ["help with", "assist with", "work on", "handle", "deal with", "thoroughly"]
    vague_count = sum(1 for term in vague_terms if term in goal_lower)
    score -= vague_count * 3

    return max(0, min(score, 25))


def score_termination_criteria(goal: str) -> int:
    """
    Score termination criteria (0-15 points).

    Checks for explicit stop conditions in the goal/prompt.
    """
    if not goal.strip():
        return 0

    goal_lower = goal.lower()
    score = 0

    # Strong termination signals (explicit STOP)
    strong_patterns = [
        (r"\bstop\s+when\b", 12),
        (r"\bstop\s+if\b", 10),
        (r"\bstop\s+after\b", 10),
        (r"\bfinish\s+when\b", 9),
        (r"\bcomplete\s+when\b", 9),
    ]

    for pattern, points in strong_patterns:
        if re.search(pattern, goal_lower):
            score = max(score, points)

    # Moderate termination signals
    moderate_patterns = [
        (r"\buntil\s+you\s+(have|find|get)\b", 8),
        (r"\bup\s+to\s+\d+", 8),
        (r"\bmax(imum)?\s+\d+", 7),
        (r"\bno\s+more\s+than\s+\d+", 7),
        (r"\bexhaust\b", 6),
        (r"\bor\s+(exhaust|stop|return)\b", 5),
        (r"\btry\s+up\s+to\b", 7),
        (r"\breturn\s+(best|results|when)\b", 5),
    ]

    for pattern, points in moderate_patterns:
        if re.search(pattern, goal_lower):
            score = max(score, points)

    # Bonus for multiple termination conditions
    all_patterns = strong_patterns + moderate_patterns
    match_count = sum(1 for pattern, _ in all_patterns if re.search(pattern, goal_lower))
    if match_count >= 2:
        score += 4

    return min(score, 15)


def score_boundaries(config: AgentConfig) -> int:
    """
    Score explicit boundaries/constraints (0-20 points).

    Checks for DO NOT, NEVER, ONLY, and role boundary statements.
    """
    text = f"{config.goal} {config.backstory} {config.system_prompt} {config.system_message}".lower()

    if not text.strip():
        return 0

    score = 0
    has_any_boundary = False

    # DO NOT constraints (strong boundary signal)
    do_not_count = len(re.findall(r"\bdo\s+not\b", text))
    if do_not_count > 0:
        has_any_boundary = True
        score += 6 + min(do_not_count - 1, 2) * 3  # 6 for first, +3 for each additional (max 12)

    # NEVER constraints (strong boundary signal)
    never_count = len(re.findall(r"\bnever\b", text))
    if never_count > 0:
        has_any_boundary = True
        score += 8 + min(never_count - 1, 2) * 4  # 8 for first, +4 for each additional

    # ONLY constraints (positive boundaries)
    only_count = len(re.findall(r"\bonly\b", text))
    if only_count > 0:
        has_any_boundary = True
        score += 4 + min(only_count - 1, 2) * 2

    # Role boundary statements
    role_boundary_patterns = [
        r"not\s+your\s+(job|responsibility|role)",
        r"is\s+not\s+your",
        r"that'?s\s+(for\s+)?the\s+\w+('s)?\s+(job|responsibility|role)",
        r"hand\s+(off|over)\s+to",
        r"leave\s+(that|this)\s+to",
    ]
    for pattern in role_boundary_patterns:
        if re.search(pattern, text):
            has_any_boundary = True
            score += 5

    # Small base score if any boundary exists
    if has_any_boundary and score < 5:
        score = 5

    return min(score, 20)


def score_tool_guidance(config: AgentConfig) -> int:
    """
    Score tool usage guidance (0-15 points).

    If agent has tools, checks for guidance on when/how to use them.
    """
    if not config.tools:
        return 10  # Neutral score if no tools

    text = f"{config.goal} {config.backstory} {config.system_prompt} {config.system_message}".lower()

    # Base score for having tools defined (not 0)
    score = 3

    # Check for explicit tool mentions with guidance
    for tool in config.tools:
        # Handle both string tools and dict tools (some frameworks use dicts)
        if isinstance(tool, dict):
            tool_name = tool.get("name", str(tool))
        else:
            tool_name = str(tool)

        tool_lower = tool_name.lower()
        # Also try with underscores/hyphens replaced
        tool_variants = [tool_lower, tool_lower.replace("_", " "), tool_lower.replace("-", " ")]

        for variant in tool_variants:
            # Look for patterns like "use X for Y" or "X: use for Y" or "X for Y"
            patterns = [
                rf"use\s+{re.escape(variant)}\s+(for|when|to)\b",
                rf"{re.escape(variant)}\s*:\s*(use\s+)?(for|when|to)\b",
                rf"{re.escape(variant)}\s+(for|when|to)\b",
            ]
            if any(re.search(p, text) for p in patterns):
                score += 5
                break

    # Check for general tool guidance patterns
    guidance_patterns = [
        r"use\s+\w+\s+for\b",
        r"when\s+to\s+use\b",
        r"for\s+\w+,?\s+use\b",
    ]
    guidance_matches = sum(1 for p in guidance_patterns if re.search(p, text))
    score += min(guidance_matches * 2, 4)

    return min(score, 15)


def score_handoff_clarity(config: AgentConfig) -> int:
    """
    Score handoff clarity (0-10 points).

    Only applies to multi-agent setups.
    """
    if not config.is_multi_agent:
        return 10  # Full score for single-agent

    text = f"{config.backstory} {config.system_prompt} {config.system_message}".lower()
    score = 0

    # Check for handoff language (allow words between key terms)
    handoff_patterns = [
        (r"hand\s+(off|over)\b.{0,30}\bto\s+the", 7),  # "hand off X to the Y"
        (r"hand\s+(off|over)\s+to", 6),
        (r"pass(es)?\s+.{0,20}\bto\s+the", 5),
        (r"for\s+the\s+\w+\s+(agent|team)", 4),
        (r"(receives?|gets?)\s+from", 4),
        (r"coordinates?\s+with", 3),
        (r"to\s+the\s+\w+\s+agent", 4),
    ]

    for pattern, points in handoff_patterns:
        if re.search(pattern, text):
            score = max(score, points)  # Take highest matching pattern

    return min(score, 10)


# =============================================================================
# Analyzer & Optimizer Classes
# =============================================================================

class AgentScorer:
    """Scores agent configurations based on the agent-specific rubric."""

    def score(self, config: AgentConfig) -> ScoringResult:
        """Score an agent configuration."""
        breakdown = {
            "role_specificity": score_role_specificity(config.role or config.name),
            "goal_clarity": score_goal_clarity(
                config.goal or config.system_prompt or config.system_message
            ),
            "termination_criteria": score_termination_criteria(
                f"{config.goal} {config.system_prompt} {config.system_message}"
            ),
            "boundaries": score_boundaries(config),
            "tool_guidance": score_tool_guidance(config),
            "handoff_clarity": score_handoff_clarity(config),
        }

        total = sum(breakdown.values())
        issues = self._identify_issues(breakdown, config)
        recommendations = self._generate_recommendations(issues)

        return ScoringResult(
            total_score=total,
            breakdown=breakdown,
            issues=issues,
            recommendations=recommendations,
        )

    def _identify_issues(self, breakdown: dict, config: AgentConfig) -> list[dict]:
        """Identify issues based on low scores."""
        issues = []

        if breakdown["role_specificity"] < 10:
            issues.append({
                "category": "role_specificity",
                "severity": "high" if breakdown["role_specificity"] < 5 else "medium",
                "description": "Role is too generic. Add domain expertise and specificity.",
            })

        if breakdown["goal_clarity"] < 12:
            issues.append({
                "category": "goal_clarity",
                "severity": "high" if breakdown["goal_clarity"] < 8 else "medium",
                "description": "Goal lacks specific deliverables or output format.",
            })

        if breakdown["termination_criteria"] < 5:
            issues.append({
                "category": "termination_missing",
                "severity": "high",
                "description": "No termination criteria. Agent may loop indefinitely.",
            })

        if breakdown["boundaries"] < 8:
            issues.append({
                "category": "no_boundaries",
                "severity": "medium",
                "description": "No explicit constraints on what the agent should NOT do.",
            })

        if config.tools and breakdown["tool_guidance"] < 8:
            issues.append({
                "category": "tool_guidance_missing",
                "severity": "medium",
                "description": "Tools available but no guidance on when to use each.",
            })

        if config.is_multi_agent and breakdown["handoff_clarity"] < 5:
            issues.append({
                "category": "handoff_missing",
                "severity": "high",
                "description": "Multi-agent setup but unclear handoff to other agents.",
            })

        # AutoGen-specific: missing description
        if config.framework == "autogen" and not config.description:
            issues.append({
                "category": "missing_description",
                "severity": "medium",
                "description": "AutoGen agent missing 'description' for GroupChat routing.",
            })

        return issues

    def _generate_recommendations(self, issues: list[dict]) -> list[str]:
        """Generate recommendations based on issues."""
        recs = []
        for issue in issues:
            if issue["category"] == "role_specificity":
                recs.append("Add domain expertise and seniority to the role (e.g., 'Senior X Analyst specializing in Y')")
            elif issue["category"] == "termination_missing":
                recs.append("Add explicit STOP conditions (e.g., 'STOP when you have 5 results')")
            elif issue["category"] == "no_boundaries":
                recs.append("Add DO NOT / NEVER constraints to prevent scope creep")
            elif issue["category"] == "goal_clarity":
                recs.append("Quantify deliverables and specify output format")
        return recs


class AgentAnalyzer:
    """Analyzes agent configurations and provides scores."""

    def __init__(self):
        self.scorer = AgentScorer()

    def analyze(self, config_str: str) -> ScoringResult:
        """Analyze an agent configuration string."""
        detection = detect_framework(config_str)

        if detection.framework == "crewai":
            config = parse_crewai_config(config_str)
        elif detection.framework == "autogen":
            config = parse_autogen_config(config_str)
        elif detection.framework == "langgraph":
            config = parse_langgraph_config(config_str)
        else:
            # Generic system prompt
            config = AgentConfig(
                framework="generic",
                system_prompt=config_str.strip()
            )

        return self.scorer.score(config)


class AgentOptimizer:
    """Optimizes agent configurations using LLM."""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.analyzer = AgentAnalyzer()

    def optimize(self, config_str: str) -> AgentOptimizationResult:
        """Optimize an agent configuration."""
        # Score original
        original_result = self.analyzer.analyze(config_str)

        # TODO: Call LLM to optimize
        # For now, return a placeholder
        if self.llm_client:
            # This will be implemented with actual LLM call
            response = self.llm_client.complete_chat([
                {"role": "system", "content": "You are an expert at optimizing AI agent prompts."},
                {"role": "user", "content": f"Optimize this agent config:\n{config_str}"}
            ])
            # Parse response and create optimized config
            optimized_config = config_str  # Placeholder
            optimized_result = self.analyzer.analyze(optimized_config)
        else:
            optimized_config = config_str
            optimized_result = original_result

        return AgentOptimizationResult(
            original_config=config_str,
            optimized_config=optimized_config,
            original_score=original_result.total_score,
            optimized_score=optimized_result.total_score,
            improvements=[],
            reasoning="Optimization not yet implemented",
        )
