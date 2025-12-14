"""Schemas for agent endpoints."""

from pydantic import BaseModel


class PlanRequest(BaseModel):
    """Request to create an execution plan."""
    user_request: str


class PlanStepResponse(BaseModel):
    """A single step in an execution plan."""
    skill: str
    input_mapping: dict[str, str] = {}
    notes: str = ""


class PlanResponse(BaseModel):
    """Response containing an execution plan."""
    reasoning: str
    steps: list[PlanStepResponse]
    is_valid: bool
    errors: list[str] = []


class ExecuteRequest(BaseModel):
    """Request to execute a skill."""
    skill: str
    input: str
    variables: dict[str, str] = {}


class ExecuteResponse(BaseModel):
    """Response from skill execution."""
    content: str
    model: str
    usage: dict[str, int] = {}
    skill: str


class EvaluateRequest(BaseModel):
    """Request to evaluate a response."""
    request: str
    response: str
    rubric: str | None = None


class JudgmentResponse(BaseModel):
    """Response containing evaluation judgment."""
    scores: dict[str, int]
    overall_score: int
    passed: bool
    strengths: list[str]
    weaknesses: list[str]
    reasoning: str


class CompareRequest(BaseModel):
    """Request to compare two responses."""
    request: str
    response_a: str
    response_b: str
    rubric: str | None = None


class CompareResponse(BaseModel):
    """Response from pairwise comparison."""
    winner: str  # "A", "B", or "tie"
    confidence: str  # "high", "medium", "low"
    comparison: dict[str, dict]
    reasoning: str


class SkillResponse(BaseModel):
    """Response containing skill information."""
    name: str
    description: str
    tags: list[str]
    model: str
    max_tokens: int
    temperature: float


class SkillListResponse(BaseModel):
    """Response containing list of skills."""
    skills: list[SkillResponse]
    total: int


# Optimization schemas

class AnalyzeRequest(BaseModel):
    """Request to analyze a prompt."""
    prompt_template: str
    task_description: str


class AnalysisIssue(BaseModel):
    """A single issue found in prompt analysis."""
    category: str
    description: str
    severity: str


class AnalysisResponse(BaseModel):
    """Response containing prompt analysis."""
    issues: list[AnalysisIssue]
    strengths: list[str]
    overall_quality: str
    priority_improvements: list[str]


class OptimizeRequest(BaseModel):
    """Request to optimize a prompt."""
    prompt_template: str
    task_description: str
    sample_inputs: list[str] = []
    skill_name: str | None = None  # If loading from registry


class OptimizeResponse(BaseModel):
    """Response containing optimized prompt."""
    original_prompt: str
    optimized_prompt: str
    original_score: float
    optimized_score: float
    improvements: list[str]
    reasoning: str
    analysis: AnalysisResponse | None = None
