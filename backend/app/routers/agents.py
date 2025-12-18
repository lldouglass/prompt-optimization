"""Router for agent endpoints."""

import json
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Add project root to path for agent imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from agents import Planner, LegacyJudge, PromptOptimizer
from agents.hallucination_checker import HallucinationChecker
from llm import OpenAIClient, MockLLMClient
from prompts import SkillRegistry

from ..database import get_db
from ..models.organization import Organization
from ..models.optimization import PromptOptimization
from ..auth import get_api_key, get_current_org
from ..models.api_key import ApiKey
from ..usage import check_and_increment_usage
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
    FewShotExampleResponse,
    FewShotResearchResponse,
    SaveOptimizationRequest,
    SavedOptimizationResponse,
    OptimizationListResponse,
    HallucinationReport,
    ClaimVerification,
)

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])

_registry = None
_llm_client = None


def get_registry() -> SkillRegistry:
    global _registry
    if _registry is None:
        _registry = SkillRegistry()
    return _registry


def get_llm_client():
    global _llm_client
    if _llm_client is None:
        try:
            _llm_client = OpenAIClient()
        except ValueError:
            _llm_client = MockLLMClient()
    return _llm_client


@router.post("/plan", response_model=PlanResponse)
async def create_plan(request: PlanRequest) -> PlanResponse:
    registry = get_registry()
    llm = get_llm_client()
    planner = Planner(llm, registry)
    plan = planner.plan(request.user_request)
    is_valid, errors = planner.validate_plan(plan)
    return PlanResponse(
        reasoning=plan.reasoning,
        steps=[PlanStepResponse(skill=step.skill, input_mapping=step.input_mapping, notes=step.notes) for step in plan.steps],
        is_valid=is_valid,
        errors=errors,
    )


@router.post("/execute", response_model=ExecuteResponse)
async def execute_skill(request: ExecuteRequest) -> ExecuteResponse:
    registry = get_registry()
    llm = get_llm_client()
    skill = registry.get(request.skill)
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Skill not found: {request.skill}")
    prompt = skill.render(input=request.input, **request.variables)
    response = llm.complete(prompt, model=skill.model, max_tokens=skill.max_tokens, temperature=skill.temperature)
    return ExecuteResponse(content=response.content, model=response.model, usage=response.usage, skill=request.skill)


@router.post("/evaluate", response_model=JudgmentResponse)
async def evaluate_response(request: EvaluateRequest) -> JudgmentResponse:
    llm = get_llm_client()
    judge = LegacyJudge(llm, rubric=request.rubric)
    judgment = judge.evaluate(request.request, request.response)

    # Run hallucination check
    checker = HallucinationChecker()
    hallucination_report = await checker.check(request.request, request.response)

    return JudgmentResponse(
        scores=judgment.scores,
        overall_score=judgment.overall_score,
        passed=judgment.passed,
        strengths=judgment.strengths,
        weaknesses=judgment.weaknesses,
        reasoning=judgment.reasoning,
        hallucination_check=HallucinationReport(
            has_hallucinations=hallucination_report.has_hallucinations,
            verified_claims=[
                ClaimVerification(claim=c.claim, status=c.status, evidence=c.evidence, source=c.source)
                for c in hallucination_report.verified_claims
            ],
            contradicted_claims=[
                ClaimVerification(claim=c.claim, status=c.status, evidence=c.evidence, source=c.source)
                for c in hallucination_report.contradicted_claims
            ],
            unverified_claims=[
                ClaimVerification(claim=c.claim, status=c.status, evidence=c.evidence, source=c.source)
                for c in hallucination_report.unverified_claims
            ],
            summary=hallucination_report.summary,
        )
    )


@router.post("/compare", response_model=CompareResponse)
async def compare_responses(request: CompareRequest) -> CompareResponse:
    llm = get_llm_client()
    judge = LegacyJudge(llm, rubric=request.rubric)
    result = judge.compare(request.request, request.response_a, request.response_b)

    # Run hallucination checks on both responses
    checker = HallucinationChecker()
    report_a = await checker.check(request.request, request.response_a)
    report_b = await checker.check(request.request, request.response_b)

    def convert_report(report) -> HallucinationReport:
        return HallucinationReport(
            has_hallucinations=report.has_hallucinations,
            verified_claims=[
                ClaimVerification(claim=c.claim, status=c.status, evidence=c.evidence, source=c.source)
                for c in report.verified_claims
            ],
            contradicted_claims=[
                ClaimVerification(claim=c.claim, status=c.status, evidence=c.evidence, source=c.source)
                for c in report.contradicted_claims
            ],
            unverified_claims=[
                ClaimVerification(claim=c.claim, status=c.status, evidence=c.evidence, source=c.source)
                for c in report.unverified_claims
            ],
            summary=report.summary,
        )

    return CompareResponse(
        winner=result.winner,
        confidence=result.confidence,
        comparison=result.comparison,
        reasoning=result.reasoning,
        hallucination_check_a=convert_report(report_a),
        hallucination_check_b=convert_report(report_b),
    )


@router.get("/skills", response_model=SkillListResponse)
async def list_skills() -> SkillListResponse:
    registry = get_registry()
    skills = registry.get_all()
    return SkillListResponse(skills=[SkillResponse(name=s.name, description=s.description, tags=s.tags, model=s.model, max_tokens=s.max_tokens, temperature=s.temperature) for s in skills], total=len(skills))


@router.get("/skills/{skill_name}", response_model=SkillResponse)
async def get_skill(skill_name: str) -> SkillResponse:
    registry = get_registry()
    skill = registry.get(skill_name)
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Skill not found: {skill_name}")
    return SkillResponse(name=skill.name, description=skill.description, tags=skill.tags, model=skill.model, max_tokens=skill.max_tokens, temperature=skill.temperature)


@router.get("/skills/tag/{tag}", response_model=SkillListResponse)
async def get_skills_by_tag(tag: str) -> SkillListResponse:
    registry = get_registry()
    skills = registry.get_by_tag(tag)
    return SkillListResponse(skills=[SkillResponse(name=s.name, description=s.description, tags=s.tags, model=s.model, max_tokens=s.max_tokens, temperature=s.temperature) for s in skills], total=len(skills))


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_prompt(request: AnalyzeRequest) -> AnalysisResponse:
    optimizer = PromptOptimizer()
    analysis = optimizer.analyze(request.prompt_template, request.task_description)
    return AnalysisResponse(
        issues=[AnalysisIssue(category=issue.get("category", "unknown"), description=issue.get("description", ""), severity=issue.get("severity", "medium")) for issue in analysis.issues],
        strengths=analysis.strengths, overall_quality=analysis.overall_quality, priority_improvements=analysis.priority_improvements)


@router.post("/optimize", response_model=OptimizeResponse)
async def optimize_prompt(
    request: OptimizeRequest,
    api_key: ApiKey = Depends(get_api_key),
    db: AsyncSession = Depends(get_db),
) -> OptimizeResponse:
    # Check and increment optimization usage
    await check_and_increment_usage(str(api_key.org_id), db, "optimizations")

    registry = get_registry()
    optimizer = PromptOptimizer()
    prompt_template = request.prompt_template
    if request.skill_name:
        skill = registry.get(request.skill_name)
        if not skill:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Skill not found: {request.skill_name}")
        prompt_template = skill.prompt_template
    result = optimizer.optimize(prompt_template=prompt_template, task_description=request.task_description, sample_inputs=request.sample_inputs if request.sample_inputs else None)
    analysis_response = None
    if result.analysis:
        analysis_response = AnalysisResponse(
            issues=[AnalysisIssue(category=issue.get("category", "unknown"), description=issue.get("description", ""), severity=issue.get("severity", "medium")) for issue in result.analysis.issues],
            strengths=result.analysis.strengths, overall_quality=result.analysis.overall_quality, priority_improvements=result.analysis.priority_improvements)

    few_shot_response = None
    if result.few_shot_research:
        examples_list = []
        for ex in result.few_shot_research.examples:
            output_str = ex.output if isinstance(ex.output, str) else json.dumps(ex.output, indent=2)
            examples_list.append(FewShotExampleResponse(
                input=ex.input,
                output=output_str,
                rationale=ex.rationale
            ))
        few_shot_response = FewShotResearchResponse(
            examples=examples_list,
            format_recommendation=result.few_shot_research.format_recommendation,
            research_notes=result.few_shot_research.research_notes
        )

    return OptimizeResponse(original_prompt=result.original_prompt, optimized_prompt=result.optimized_prompt, original_score=result.original_score, optimized_score=result.optimized_score, improvements=result.improvements, reasoning=result.reasoning, analysis=analysis_response, few_shot_research=few_shot_response)


@router.post("/optimizations", response_model=SavedOptimizationResponse)
async def save_optimization(
    request: SaveOptimizationRequest,
    api_key: ApiKey = Depends(get_api_key),
    db: AsyncSession = Depends(get_db)
) -> SavedOptimizationResponse:
    """Save an optimization result to the database."""
    optimization = PromptOptimization(
        org_id=api_key.org_id,
        original_prompt=request.original_prompt,
        optimized_prompt=request.optimized_prompt,
        task_description=request.task_description,
        original_score=request.original_score,
        optimized_score=request.optimized_score,
        improvements=request.improvements,
        reasoning=request.reasoning,
        skill_name=request.skill_name,
        analysis=request.analysis.model_dump() if request.analysis else None,
    )
    db.add(optimization)
    await db.commit()
    await db.refresh(optimization)
    return SavedOptimizationResponse(
        id=str(optimization.id),
        original_prompt=optimization.original_prompt,
        optimized_prompt=optimization.optimized_prompt,
        task_description=optimization.task_description,
        original_score=optimization.original_score,
        optimized_score=optimization.optimized_score,
        improvements=optimization.improvements,
        reasoning=optimization.reasoning,
        skill_name=optimization.skill_name,
        model_used=optimization.model_used,
        created_at=optimization.created_at.isoformat(),
        analysis=request.analysis,
    )


@router.get("/optimizations", response_model=OptimizationListResponse)
async def list_optimizations(
    limit: int = 20,
    offset: int = 0,
    api_key: ApiKey = Depends(get_api_key),
    db: AsyncSession = Depends(get_db)
) -> OptimizationListResponse:
    """List saved optimizations with pagination, filtered by organization."""
    # Count total for this organization
    count_result = await db.execute(
        select(PromptOptimization).where(PromptOptimization.org_id == api_key.org_id)
    )
    total = len(count_result.scalars().all())

    # Get paginated results for this organization
    result = await db.execute(
        select(PromptOptimization)
        .where(PromptOptimization.org_id == api_key.org_id)
        .order_by(PromptOptimization.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    optimizations = result.scalars().all()
    return OptimizationListResponse(
        optimizations=[
            SavedOptimizationResponse(
                id=str(opt.id),
                original_prompt=opt.original_prompt,
                optimized_prompt=opt.optimized_prompt,
                task_description=opt.task_description,
                original_score=opt.original_score,
                optimized_score=opt.optimized_score,
                improvements=opt.improvements,
                reasoning=opt.reasoning,
                skill_name=opt.skill_name,
                model_used=opt.model_used,
                created_at=opt.created_at.isoformat(),
                analysis=AnalysisResponse(**opt.analysis) if opt.analysis else None,
            )
            for opt in optimizations
        ],
        total=total,
    )


@router.get("/optimizations/{optimization_id}", response_model=SavedOptimizationResponse)
async def get_optimization(optimization_id: str, db: AsyncSession = Depends(get_db)) -> SavedOptimizationResponse:
    """Get a specific saved optimization by ID."""
    result = await db.execute(select(PromptOptimization).where(PromptOptimization.id == optimization_id))
    optimization = result.scalar_one_or_none()
    if not optimization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Optimization not found: {optimization_id}")
    return SavedOptimizationResponse(
        id=str(optimization.id),
        original_prompt=optimization.original_prompt,
        optimized_prompt=optimization.optimized_prompt,
        task_description=optimization.task_description,
        original_score=optimization.original_score,
        optimized_score=optimization.optimized_score,
        improvements=optimization.improvements,
        reasoning=optimization.reasoning,
        skill_name=optimization.skill_name,
        model_used=optimization.model_used,
        created_at=optimization.created_at.isoformat(),
        analysis=AnalysisResponse(**optimization.analysis) if optimization.analysis else None,
    )
