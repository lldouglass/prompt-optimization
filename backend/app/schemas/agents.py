"""Schemas for agent endpoints."""

from typing import Literal
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


class ClaimVerification(BaseModel):
    """A single verified or unverified claim."""
    claim: str
    status: str  # "verified", "contradicted", "unverified"
    evidence: str
    source: str | None = None


class HallucinationReport(BaseModel):
    """Report on hallucination detection."""
    has_hallucinations: bool
    verified_claims: list[ClaimVerification] = []
    contradicted_claims: list[ClaimVerification] = []
    unverified_claims: list[ClaimVerification] = []
    summary: str


class JudgmentResponse(BaseModel):
    """Response containing evaluation judgment."""
    scores: dict[str, int]
    overall_score: int
    passed: bool
    strengths: list[str]
    weaknesses: list[str]
    reasoning: str
    hallucination_check: HallucinationReport | None = None


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
    hallucination_check_a: HallucinationReport | None = None
    hallucination_check_b: HallucinationReport | None = None


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


class FewShotExampleResponse(BaseModel):
    """A single few-shot example."""
    input: str
    output: str
    rationale: str = ""


class FewShotResearchResponse(BaseModel):
    """Research results for few-shot examples."""
    examples: list[FewShotExampleResponse] = []
    format_recommendation: str = ""
    research_notes: str = ""


class OptimizeRequest(BaseModel):
    """Request to optimize a prompt."""
    prompt_template: str
    task_description: str
    sample_inputs: list[str] = []
    skill_name: str | None = None  # If loading from registry
    mode: Literal["standard", "enhanced"] | None = None  # None = auto-detect from tier


class WebSourceResponse(BaseModel):
    """A web source used for few-shot research."""
    url: str
    title: str
    content: str


class JudgeEvaluationResponse(BaseModel):
    """Judge evaluation results for optimization quality."""
    judge_score: float
    is_improvement: bool
    improvement_margin: str | None = None  # "slightly", "moderately", "strongly"
    tags: list[str] = []
    rationale: str = ""
    has_regressions: bool = False
    regression_details: str = ""


class OptimizeResponse(BaseModel):
    """Response containing optimized prompt."""
    original_prompt: str
    optimized_prompt: str
    original_score: float
    optimized_score: float
    improvements: list[str]
    reasoning: str
    analysis: AnalysisResponse | None = None
    few_shot_research: FewShotResearchResponse | None = None
    # Enhanced mode fields
    mode: str = "standard"
    web_sources: list[WebSourceResponse] | None = None
    judge_evaluation: JudgeEvaluationResponse | None = None
    iterations_used: int = 1


class SaveOptimizationRequest(BaseModel):
    """Request to save an optimization result."""
    original_prompt: str
    optimized_prompt: str
    task_description: str
    original_score: float
    optimized_score: float
    improvements: list[str] = []
    reasoning: str = ""
    analysis: AnalysisResponse | None = None
    skill_name: str | None = None


class SavedOptimizationResponse(BaseModel):
    """Response for a saved optimization."""
    id: str
    original_prompt: str
    optimized_prompt: str
    task_description: str
    original_score: float
    optimized_score: float
    improvements: list[str]
    reasoning: str
    analysis: AnalysisResponse | None = None
    skill_name: str | None = None
    model_used: str
    created_at: str


class OptimizationListResponse(BaseModel):
    """Response containing list of saved optimizations."""
    optimizations: list[SavedOptimizationResponse]
    total: int


# Saved Evaluation schemas

class SaveEvaluationRequest(BaseModel):
    """Request to save an evaluation."""
    request: str
    response: str
    model_name: str | None = None
    judgment: JudgmentResponse
    hallucination_check: HallucinationReport | None = None


class SaveComparisonRequest(BaseModel):
    """Request to save a comparison."""
    request: str
    response_a: str
    response_b: str
    model_a: str | None = None
    model_b: str | None = None
    comparison_result: CompareResponse


class SavedEvaluationResponse(BaseModel):
    """Response for a saved evaluation."""
    id: str
    eval_type: str
    request: str
    response: str | None = None
    model_name: str | None = None
    response_a: str | None = None
    response_b: str | None = None
    model_a: str | None = None
    model_b: str | None = None
    judgment: dict | None = None
    hallucination_check: dict | None = None
    comparison_result: dict | None = None
    hallucination_check_a: dict | None = None
    hallucination_check_b: dict | None = None
    created_at: str


class EvaluationListResponse(BaseModel):
    """Response containing list of saved evaluations."""
    evaluations: list[SavedEvaluationResponse]
    total: int
