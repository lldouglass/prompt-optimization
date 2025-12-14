"""Router for agent endpoints."""

import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException, status

# Add project root to path for agent imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from agents import Planner, LegacyJudge, PromptOptimizer
from llm import OpenAIClient, MockLLMClient
from prompts import SkillRegistry

from ..schemas.agents import (
    PlanRequest,
    PlanResponse,
    PlanStepResponse,
    ExecuteRequest,
    ExecuteResponse,
    EvaluateRequest,
    JudgmentResponse,
    CompareRequest,
    CompareResponse,
    SkillResponse,
    SkillListResponse,
    AnalyzeRequest,
    AnalysisResponse,
    AnalysisIssue,
    OptimizeRequest,
    OptimizeResponse,
)

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])

# Initialize components (singleton pattern)
_registry = None
_llm_client = None


def get_registry() -> SkillRegistry:
    """Get or create the skill registry."""
    global _registry
    if _registry is None:
        _registry = SkillRegistry()
    return _registry


def get_llm_client():
    """Get or create the LLM client."""
    global _llm_client
    if _llm_client is None:
        try:
            _llm_client = OpenAIClient()
        except ValueError:
            # Fall back to mock if no API key
            _llm_client = MockLLMClient()
    return _llm_client


@router.post("/plan", response_model=PlanResponse)
async def create_plan(request: PlanRequest) -> PlanResponse:
    """
    Create an execution plan for a user request.

    Analyzes the request and selects appropriate skills.
    """
    registry = get_registry()
    llm = get_llm_client()
    planner = Planner(llm, registry)

    plan = planner.plan(request.user_request)
    is_valid, errors = planner.validate_plan(plan)

    return PlanResponse(
        reasoning=plan.reasoning,
        steps=[
            PlanStepResponse(
                skill=step.skill,
                input_mapping=step.input_mapping,
                notes=step.notes,
            )
            for step in plan.steps
        ],
        is_valid=is_valid,
        errors=errors,
    )


@router.post("/execute", response_model=ExecuteResponse)
async def execute_skill(request: ExecuteRequest) -> ExecuteResponse:
    """
    Execute a specific skill with the given input.
    """
    registry = get_registry()
    llm = get_llm_client()

    skill = registry.get(request.skill)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill not found: {request.skill}",
        )

    # Render the prompt with input and variables
    prompt = skill.render(input=request.input, **request.variables)

    # Call the LLM
    response = llm.complete(
        prompt,
        model=skill.model,
        max_tokens=skill.max_tokens,
        temperature=skill.temperature,
    )

    return ExecuteResponse(
        content=response.content,
        model=response.model,
        usage=response.usage,
        skill=request.skill,
    )


@router.post("/evaluate", response_model=JudgmentResponse)
async def evaluate_response(request: EvaluateRequest) -> JudgmentResponse:
    """
    Evaluate a response according to a rubric.
    """
    llm = get_llm_client()
    judge = LegacyJudge(llm, rubric=request.rubric)

    judgment = judge.evaluate(request.request, request.response)

    return JudgmentResponse(
        scores=judgment.scores,
        overall_score=judgment.overall_score,
        passed=judgment.passed,
        strengths=judgment.strengths,
        weaknesses=judgment.weaknesses,
        reasoning=judgment.reasoning,
    )


@router.post("/compare", response_model=CompareResponse)
async def compare_responses(request: CompareRequest) -> CompareResponse:
    """
    Compare two responses to determine which is better.
    """
    llm = get_llm_client()
    judge = LegacyJudge(llm, rubric=request.rubric)

    result = judge.compare(request.request, request.response_a, request.response_b)

    return CompareResponse(
        winner=result.winner,
        confidence=result.confidence,
        comparison=result.comparison,
        reasoning=result.reasoning,
    )


@router.get("/skills", response_model=SkillListResponse)
async def list_skills() -> SkillListResponse:
    """
    List all available skills.
    """
    registry = get_registry()
    skills = registry.get_all()

    return SkillListResponse(
        skills=[
            SkillResponse(
                name=s.name,
                description=s.description,
                tags=s.tags,
                model=s.model,
                max_tokens=s.max_tokens,
                temperature=s.temperature,
            )
            for s in skills
        ],
        total=len(skills),
    )


@router.get("/skills/{skill_name}", response_model=SkillResponse)
async def get_skill(skill_name: str) -> SkillResponse:
    """
    Get a specific skill by name.
    """
    registry = get_registry()
    skill = registry.get(skill_name)

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill not found: {skill_name}",
        )

    return SkillResponse(
        name=skill.name,
        description=skill.description,
        tags=skill.tags,
        model=skill.model,
        max_tokens=skill.max_tokens,
        temperature=skill.temperature,
    )


@router.get("/skills/tag/{tag}", response_model=SkillListResponse)
async def get_skills_by_tag(tag: str) -> SkillListResponse:
    """
    Get skills filtered by tag.
    """
    registry = get_registry()
    skills = registry.get_by_tag(tag)

    return SkillListResponse(
        skills=[
            SkillResponse(
                name=s.name,
                description=s.description,
                tags=s.tags,
                model=s.model,
                max_tokens=s.max_tokens,
                temperature=s.temperature,
            )
            for s in skills
        ],
        total=len(skills),
    )


# Prompt Optimization endpoints

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_prompt(request: AnalyzeRequest) -> AnalysisResponse:
    """
    Analyze a prompt template and identify optimization opportunities.

    Returns issues, strengths, and priority improvements.
    """
    optimizer = PromptOptimizer()
    analysis = optimizer.analyze(request.prompt_template, request.task_description)

    return AnalysisResponse(
        issues=[
            AnalysisIssue(
                category=issue.get("category", "unknown"),
                description=issue.get("description", ""),
                severity=issue.get("severity", "medium"),
            )
            for issue in analysis.issues
        ],
        strengths=analysis.strengths,
        overall_quality=analysis.overall_quality,
        priority_improvements=analysis.priority_improvements,
    )


@router.post("/optimize", response_model=OptimizeResponse)
async def optimize_prompt(request: OptimizeRequest) -> OptimizeResponse:
    """
    Optimize a prompt template using best practices.

    Analyzes the prompt, scores it, generates an optimized version,
    and scores the optimized version to verify improvement.

    Supports loading prompts from the skill registry by name.
    """
    registry = get_registry()
    optimizer = PromptOptimizer()

    # Get prompt from registry if skill_name provided
    prompt_template = request.prompt_template
    if request.skill_name:
        skill = registry.get(request.skill_name)
        if not skill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Skill not found: {request.skill_name}",
            )
        prompt_template = skill.prompt_template

    # Run optimization
    result = optimizer.optimize(
        prompt_template=prompt_template,
        task_description=request.task_description,
        sample_inputs=request.sample_inputs if request.sample_inputs else None,
    )

    # Build analysis response if available
    analysis_response = None
    if result.analysis:
        analysis_response = AnalysisResponse(
            issues=[
                AnalysisIssue(
                    category=issue.get("category", "unknown"),
                    description=issue.get("description", ""),
                    severity=issue.get("severity", "medium"),
                )
                for issue in result.analysis.issues
            ],
            strengths=result.analysis.strengths,
            overall_quality=result.analysis.overall_quality,
            priority_improvements=result.analysis.priority_improvements,
        )

    return OptimizeResponse(
        original_prompt=result.original_prompt,
        optimized_prompt=result.optimized_prompt,
        original_score=result.original_score,
        optimized_score=result.optimized_score,
        improvements=result.improvements,
        reasoning=result.reasoning,
        analysis=analysis_response,
    )
