"""Router for agent endpoints."""

import json
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Add project root to path for agent imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from agents import Planner, LegacyJudge, PromptOptimizer, MediaOptimizer
from agents.hallucination_checker import HallucinationChecker
from llm import OpenAIClient, MockLLMClient
from llm.client import reset_usage, calculate_cost_cents
from prompts import SkillRegistry

from ..database import get_db
from ..models.organization import Organization
from ..models.optimization import PromptOptimization
from ..models.agent_session import AgentSession
from ..models.evaluation import SavedEvaluation
from ..models.feedback import UserFeedback
from ..auth import get_api_key, get_current_org, get_current_org_dual, get_user_from_session
from ..models.api_key import ApiKey
from ..usage import check_usage_limit, increment_usage
from ..schemas.feedback import (
    FeedbackCreateRequest,
    FeedbackResponse,
    FeedbackListResponse,
)
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
    UpdateOptimizationRequest,
    SavedOptimizationResponse,
    OptimizationListResponse,
    FolderResponse,
    FolderListResponse,
    HallucinationReport,
    ClaimVerification,
    SaveEvaluationRequest,
    SaveComparisonRequest,
    SavedEvaluationResponse,
    EvaluationListResponse,
    WebSourceResponse,
    JudgeEvaluationResponse,
    MediaOptimizeRequest,
    MediaOptimizeResponse,
    FileProcessingResult,
    AgentOptimizeStartRequest,
    AgentSessionResponse,
    MediaAgentStartRequest,
    MediaAgentResponse,
)
from ..services.file_processor import process_file, FileProcessingError

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


@router.post("/optimize/start", response_model=AgentSessionResponse)
async def start_agent_optimization(
    request: AgentOptimizeStartRequest,
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db),
) -> AgentSessionResponse:
    """
    Start an agent-based optimization session.

    Returns a session_id that the client uses to connect via WebSocket at:
    ws://host/ws/optimize/{session_id}

    The agent will analyze the prompt and decide whether to:
    - Search the web for examples
    - Ask the user clarification questions
    - Generate the optimized prompt
    """
    import uuid
    from datetime import datetime, timedelta

    # Check usage limit
    await check_usage_limit(str(org.id), db, "optimizations")

    # Create the session
    session = AgentSession(
        id=uuid.uuid4(),
        org_id=org.id,
        status="running",
        agent_type="optimizer",
        initial_request={
            "prompt_template": request.prompt_template,
            "task_description": request.task_description,
            "sample_inputs": request.sample_inputs,
            "output_format": request.output_format,
        },
        conversation_history=[],
        tool_calls_made=[],
        pending_questions=[],
        user_answers=[],
        questions_asked_count=0,
        web_sources=[],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(hours=1),
    )

    db.add(session)
    await db.commit()
    await db.refresh(session)

    return AgentSessionResponse(
        session_id=str(session.id),
        status="running",
        message="Session created. Connect via WebSocket to /ws/optimize/{session_id}"
    )


@router.post("/media-optimize/start", response_model=AgentSessionResponse)
async def start_media_agent_optimization(
    request: MediaAgentStartRequest,
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db),
) -> AgentSessionResponse:
    """
    Start an agent-based media prompt optimization session.

    Returns a session_id that the client uses to connect via WebSocket at:
    ws://host/ws/media-optimize/{session_id}

    The agent will analyze the prompt and decide whether to:
    - Search the web for model-specific examples
    - Ask the user clarification questions about subject, style, or model
    - Generate the optimized prompt with correct syntax for the target model
    """
    import uuid
    from datetime import datetime, timedelta

    # Check usage limit
    await check_usage_limit(str(org.id), db, "optimizations")

    # Create the session
    session = AgentSession(
        id=uuid.uuid4(),
        org_id=org.id,
        status="running",
        agent_type="media_optimizer",
        initial_request={
            "prompt": request.prompt,
            "task_description": request.task_description,
            "media_type": request.media_type,
            "target_model": request.target_model,
            "aspect_ratio": request.aspect_ratio,
            "logo_url": request.logo_url,
            "uploaded_files": [f.model_dump() for f in request.uploaded_files] if request.uploaded_files else [],
        },
        conversation_history=[],
        tool_calls_made=[],
        pending_questions=[],
        user_answers=[],
        questions_asked_count=0,
        web_sources=[],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(hours=1),
    )

    db.add(session)
    await db.commit()
    await db.refresh(session)

    return AgentSessionResponse(
        session_id=str(session.id),
        status="running",
        message="Session created. Connect via WebSocket to /ws/media-optimize/{session_id}"
    )


@router.post("/optimize", response_model=OptimizeResponse)
async def optimize_prompt(
    request: OptimizeRequest,
    fastapi_request: Request,
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db),
) -> OptimizeResponse:
    # Check usage limit FIRST (doesn't increment - that happens after success)
    await check_usage_limit(str(org.id), db, "optimizations")

    # Reset token tracking before optimization
    reset_usage()

    # Process uploaded files
    file_context_results: list[FileProcessingResult] = []
    file_context_text = ""

    if request.uploaded_files:
        for uploaded in request.uploaded_files:
            try:
                content = await process_file(
                    uploaded.file_data,
                    uploaded.file_name,
                    uploaded.mime_type
                )
                # Truncate extracted_text for response (full text goes to optimizer)
                display_text = content.text[:500] + "..." if len(content.text) > 500 else content.text
                file_context_results.append(FileProcessingResult(
                    file_name=content.file_name,
                    file_type=content.file_type,
                    extracted_text=display_text,
                    extraction_method=content.extraction_method,
                    status="success"
                ))
                file_context_text += f"\n\n--- Content from {content.file_name} ---\n{content.text}"
            except FileProcessingError as e:
                file_context_results.append(FileProcessingResult(
                    file_name=uploaded.file_name,
                    file_type="unknown",
                    extracted_text="",
                    extraction_method="none",
                    status="error",
                    error_message=str(e)
                ))

    registry = get_registry()
    optimizer = PromptOptimizer()
    prompt_template = request.prompt_template
    if request.skill_name:
        skill = registry.get(request.skill_name)
        if not skill:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Skill not found: {request.skill_name}")
        prompt_template = skill.prompt_template

    # Enhance task description with file context
    enhanced_task = request.task_description
    if file_context_text:
        enhanced_task = f"""{request.task_description}

## Reference Material (from uploaded files)
{file_context_text}

Use this reference material to inform your optimization suggestions."""

    # Use requested mode, or auto-detect (enhanced for all users)
    use_enhanced = False
    if request.mode == "enhanced":
        use_enhanced = True
    elif request.mode == "standard":
        use_enhanced = False
    else:
        # Auto-detect: use enhanced for all users
        use_enhanced = True

    # Run optimization
    if use_enhanced:
        result = await optimizer.optimize_enhanced(
            prompt_template=prompt_template,
            task_description=enhanced_task,
            sample_inputs=request.sample_inputs if request.sample_inputs else None,
            output_format=request.output_format
        )
    else:
        result = optimizer.optimize(
            prompt_template=prompt_template,
            task_description=enhanced_task,
            sample_inputs=request.sample_inputs if request.sample_inputs else None,
            output_format=request.output_format
        )

    # Track token usage for this optimization
    usage = reset_usage()
    if usage["total_tokens"] > 0:
        cost_cents = calculate_cost_cents(usage["prompt_tokens"], usage["completion_tokens"])
        org.tokens_used_this_month += usage["total_tokens"]
        org.estimated_cost_cents += cost_cents
        await db.commit()

    # Build analysis response
    analysis_response = None
    if result.analysis:
        analysis_response = AnalysisResponse(
            issues=[AnalysisIssue(category=issue.get("category", "unknown"), description=issue.get("description", ""), severity=issue.get("severity", "medium")) for issue in result.analysis.issues],
            strengths=result.analysis.strengths, overall_quality=result.analysis.overall_quality, priority_improvements=result.analysis.priority_improvements)

    # Build few-shot response
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

    # Build enhanced mode fields
    web_sources = None
    judge_evaluation = None
    iterations_used = 1
    mode = "standard"

    if use_enhanced and hasattr(result, 'web_sources'):
        mode = "enhanced"
        iterations_used = getattr(result, 'iterations_used', 1)

        # Web sources
        if result.web_sources:
            web_sources = [
                WebSourceResponse(url=s.url, title=s.title, content=s.content)
                for s in result.web_sources
            ]

        # Judge evaluation
        if result.judge_evaluation:
            judge_evaluation = JudgeEvaluationResponse(
                judge_score=result.judge_evaluation.judge_score,
                is_improvement=result.judge_evaluation.is_improvement,
                improvement_margin=result.judge_evaluation.improvement_margin,
                tags=result.judge_evaluation.tags,
                rationale=result.judge_evaluation.rationale,
                has_regressions=result.judge_evaluation.has_regressions,
                regression_details=result.judge_evaluation.regression_details
            )

    # Only increment usage AFTER successful optimization
    await increment_usage(str(org.id), db, "optimizations")

    return OptimizeResponse(
        original_prompt=result.original_prompt,
        optimized_prompt=result.optimized_prompt,
        original_score=result.original_score,
        optimized_score=result.optimized_score,
        improvements=result.improvements,
        reasoning=result.reasoning,
        analysis=analysis_response,
        few_shot_research=few_shot_response,
        mode=mode,
        web_sources=web_sources,
        judge_evaluation=judge_evaluation,
        iterations_used=iterations_used,
        file_context=file_context_results if file_context_results else None
    )




@router.post("/optimize-media", response_model=MediaOptimizeResponse)
async def optimize_media_prompt(
    request: MediaOptimizeRequest,
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db),
) -> MediaOptimizeResponse:
    """Optimize a photo or video prompt."""
    # Check usage limit FIRST (doesn't increment - that happens after success)
    await check_usage_limit(str(org.id), db, "optimizations")

    # Reset token tracking before optimization
    reset_usage()

    # Process uploaded files - reference images
    file_context_results: list[FileProcessingResult] = []
    file_context_text = ""

    if request.uploaded_files:
        for uploaded in request.uploaded_files:
            try:
                content = await process_file(
                    uploaded.file_data,
                    uploaded.file_name,
                    uploaded.mime_type
                )
                display_text = content.text[:500] + "..." if len(content.text) > 500 else content.text
                file_context_results.append(FileProcessingResult(
                    file_name=content.file_name,
                    file_type=content.file_type,
                    extracted_text=display_text,
                    extraction_method=content.extraction_method,
                    status="success"
                ))
                file_context_text += f"\n\n--- Reference from {content.file_name} ---\n{content.text}"
            except FileProcessingError as e:
                file_context_results.append(FileProcessingResult(
                    file_name=uploaded.file_name,
                    file_type="unknown",
                    extracted_text="",
                    extraction_method="none",
                    status="error",
                    error_message=str(e)
                ))

    # Enhance subject with file context if present
    enhanced_subject = request.subject
    if file_context_text:
        enhanced_subject = f"""{request.subject}

## Reference Image Analysis
{file_context_text}"""

    optimizer = MediaOptimizer()
    result = optimizer.generate_prompt(
        media_type=request.media_type,
        subject=enhanced_subject,
        style_lighting=request.style_lighting,
        issues_to_fix=request.issues_to_fix,
        constraints=request.constraints,
        camera_movement=request.camera_movement,
        shot_type=request.shot_type,
        motion_endpoints=request.motion_endpoints,
        existing_prompt=request.existing_prompt,
    )

    # Track token usage
    usage = reset_usage()
    if usage["total_tokens"] > 0:
        cost_cents = calculate_cost_cents(usage["prompt_tokens"], usage["completion_tokens"])
        org.tokens_used_this_month += usage["total_tokens"]
        org.estimated_cost_cents += cost_cents
        await db.commit()

    # Only increment usage AFTER successful optimization
    await increment_usage(str(org.id), db, "optimizations")

    return MediaOptimizeResponse(
        optimized_prompt=result.optimized_prompt,
        original_prompt=result.original_prompt,
        original_score=result.original_score,
        optimized_score=result.optimized_score,
        improvements=result.improvements,
        reasoning=result.reasoning,
        tips=result.tips,
        media_type=result.media_type,
        file_context=file_context_results if file_context_results else None
    )


def _build_optimization_response(opt: PromptOptimization) -> SavedOptimizationResponse:
    """Build a SavedOptimizationResponse from a PromptOptimization model."""
    return SavedOptimizationResponse(
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
        # Prompt Library fields
        name=opt.name,
        folder=opt.folder,
        # Media-specific fields
        media_type=opt.media_type,
        target_model=opt.target_model,
        negative_prompt=opt.negative_prompt,
        parameters=opt.parameters,
        tips=opt.tips,
        web_sources=[WebSourceResponse(**ws) for ws in opt.web_sources] if opt.web_sources else None,
        aspect_ratio=opt.aspect_ratio,
    )


@router.post("/optimizations", response_model=SavedOptimizationResponse)
async def save_optimization(
    request: SaveOptimizationRequest,
    fastapi_request: Request,
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db)
) -> SavedOptimizationResponse:
    """Save an optimization result to the database."""
    optimization = PromptOptimization(
        org_id=org.id,
        original_prompt=request.original_prompt,
        optimized_prompt=request.optimized_prompt,
        task_description=request.task_description,
        original_score=request.original_score,
        optimized_score=request.optimized_score,
        improvements=request.improvements,
        reasoning=request.reasoning,
        skill_name=request.skill_name,
        analysis=request.analysis.model_dump() if request.analysis else None,
        # Prompt Library fields
        name=request.name or request.task_description[:255],  # Default to task description
        folder=request.folder,
        # Media-specific fields
        media_type=request.media_type,
        target_model=request.target_model,
        negative_prompt=request.negative_prompt,
        parameters=request.parameters,
        tips=request.tips,
        web_sources=[ws.model_dump() for ws in request.web_sources] if request.web_sources else None,
        aspect_ratio=request.aspect_ratio,
    )
    db.add(optimization)
    await db.commit()
    await db.refresh(optimization)
    return _build_optimization_response(optimization)


@router.get("/optimizations/folders", response_model=FolderListResponse)
async def list_folders(
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db)
) -> FolderListResponse:
    """List all folders with their prompt counts."""
    from sqlalchemy import func

    result = await db.execute(
        select(
            PromptOptimization.folder,
            func.count(PromptOptimization.id).label("count")
        )
        .where(PromptOptimization.org_id == org.id)
        .where(PromptOptimization.folder.isnot(None))
        .where(PromptOptimization.folder != "")
        .group_by(PromptOptimization.folder)
        .order_by(PromptOptimization.folder)
    )

    folders = [
        FolderResponse(name=row.folder, count=row.count)
        for row in result.all()
    ]

    return FolderListResponse(folders=folders)


@router.get("/optimizations", response_model=OptimizationListResponse)
async def list_optimizations(
    fastapi_request: Request,
    limit: int = 20,
    offset: int = 0,
    folder: str | None = None,
    media_type: str | None = None,
    target_model: str | None = None,
    search: str | None = None,
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db)
) -> OptimizationListResponse:
    """List saved optimizations with pagination and filtering."""
    from sqlalchemy import func, or_

    # Build base query
    base_query = select(PromptOptimization).where(PromptOptimization.org_id == org.id)

    # Apply filters
    if folder is not None:
        if folder == "":  # Empty string means "unfiled"
            base_query = base_query.where(
                or_(PromptOptimization.folder.is_(None), PromptOptimization.folder == "")
            )
        else:
            base_query = base_query.where(PromptOptimization.folder == folder)

    if media_type is not None:
        if media_type == "text":
            base_query = base_query.where(PromptOptimization.media_type.is_(None))
        else:
            base_query = base_query.where(PromptOptimization.media_type == media_type)

    if target_model is not None:
        base_query = base_query.where(PromptOptimization.target_model == target_model)

    if search:
        search_pattern = f"%{search}%"
        base_query = base_query.where(
            or_(
                PromptOptimization.name.ilike(search_pattern),
                PromptOptimization.task_description.ilike(search_pattern)
            )
        )

    # Count total matching results
    count_query = select(func.count()).select_from(base_query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # Get paginated results
    result = await db.execute(
        base_query
        .order_by(PromptOptimization.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    optimizations = result.scalars().all()

    return OptimizationListResponse(
        optimizations=[_build_optimization_response(opt) for opt in optimizations],
        total=total,
    )


@router.get("/optimizations/{optimization_id}", response_model=SavedOptimizationResponse)
async def get_optimization(
    optimization_id: str,
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db)
) -> SavedOptimizationResponse:
    """Get a specific saved optimization by ID."""
    result = await db.execute(
        select(PromptOptimization)
        .where(PromptOptimization.id == optimization_id)
        .where(PromptOptimization.org_id == org.id)
    )
    optimization = result.scalar_one_or_none()
    if not optimization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Optimization not found: {optimization_id}")
    return _build_optimization_response(optimization)


@router.patch("/optimizations/{optimization_id}", response_model=SavedOptimizationResponse)
async def update_optimization(
    optimization_id: str,
    request: UpdateOptimizationRequest,
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db)
) -> SavedOptimizationResponse:
    """Update a saved optimization (name, prompt text, or folder)."""
    result = await db.execute(
        select(PromptOptimization)
        .where(PromptOptimization.id == optimization_id)
        .where(PromptOptimization.org_id == org.id)
    )
    optimization = result.scalar_one_or_none()
    if not optimization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Optimization not found: {optimization_id}")

    # Update only provided fields
    if request.name is not None:
        optimization.name = request.name
    if request.optimized_prompt is not None:
        optimization.optimized_prompt = request.optimized_prompt
    if request.folder is not None:
        optimization.folder = request.folder if request.folder else None  # Empty string -> None

    await db.commit()
    await db.refresh(optimization)
    return _build_optimization_response(optimization)


@router.delete("/optimizations/{optimization_id}")
async def delete_optimization(
    optimization_id: str,
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Delete a saved optimization."""
    result = await db.execute(
        select(PromptOptimization)
        .where(PromptOptimization.id == optimization_id)
        .where(PromptOptimization.org_id == org.id)
    )
    optimization = result.scalar_one_or_none()
    if not optimization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Optimization not found: {optimization_id}")

    await db.delete(optimization)
    await db.commit()
    return {"deleted": True}


# Saved Evaluations endpoints

@router.post("/evaluations", response_model=SavedEvaluationResponse)
async def save_evaluation(
    request: SaveEvaluationRequest,
    fastapi_request: Request,
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db)
) -> SavedEvaluationResponse:
    """Save an evaluation result to the database."""
    evaluation = SavedEvaluation(
        org_id=org.id,
        eval_type="evaluation",
        request=request.request,
        response=request.response,
        model_name=request.model_name,
        judgment=request.judgment.model_dump() if request.judgment else None,
        hallucination_check=request.hallucination_check.model_dump() if request.hallucination_check else None,
    )
    db.add(evaluation)
    await db.commit()
    await db.refresh(evaluation)
    return SavedEvaluationResponse(
        id=str(evaluation.id),
        eval_type=evaluation.eval_type,
        request=evaluation.request,
        response=evaluation.response,
        model_name=evaluation.model_name,
        judgment=evaluation.judgment,
        hallucination_check=evaluation.hallucination_check,
        created_at=evaluation.created_at.isoformat(),
    )


@router.post("/comparisons", response_model=SavedEvaluationResponse)
async def save_comparison(
    request: SaveComparisonRequest,
    fastapi_request: Request,
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db)
) -> SavedEvaluationResponse:
    """Save a comparison result to the database."""
    evaluation = SavedEvaluation(
        org_id=org.id,
        eval_type="comparison",
        request=request.request,
        response_a=request.response_a,
        response_b=request.response_b,
        model_a=request.model_a,
        model_b=request.model_b,
        comparison_result=request.comparison_result.model_dump() if request.comparison_result else None,
        hallucination_check_a=request.comparison_result.hallucination_check_a.model_dump() if request.comparison_result and request.comparison_result.hallucination_check_a else None,
        hallucination_check_b=request.comparison_result.hallucination_check_b.model_dump() if request.comparison_result and request.comparison_result.hallucination_check_b else None,
    )
    db.add(evaluation)
    await db.commit()
    await db.refresh(evaluation)
    return SavedEvaluationResponse(
        id=str(evaluation.id),
        eval_type=evaluation.eval_type,
        request=evaluation.request,
        response_a=evaluation.response_a,
        response_b=evaluation.response_b,
        model_a=evaluation.model_a,
        model_b=evaluation.model_b,
        comparison_result=evaluation.comparison_result,
        hallucination_check_a=evaluation.hallucination_check_a,
        hallucination_check_b=evaluation.hallucination_check_b,
        created_at=evaluation.created_at.isoformat(),
    )


@router.get("/evaluations", response_model=EvaluationListResponse)
async def list_evaluations(
    fastapi_request: Request,
    limit: int = 20,
    offset: int = 0,
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db)
) -> EvaluationListResponse:
    """List saved evaluations with pagination, filtered by organization."""
    count_result = await db.execute(
        select(SavedEvaluation).where(SavedEvaluation.org_id == org.id)
    )
    total = len(count_result.scalars().all())

    result = await db.execute(
        select(SavedEvaluation)
        .where(SavedEvaluation.org_id == org.id)
        .order_by(SavedEvaluation.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    evaluations = result.scalars().all()
    return EvaluationListResponse(
        evaluations=[
            SavedEvaluationResponse(
                id=str(ev.id),
                eval_type=ev.eval_type,
                request=ev.request,
                response=ev.response,
                model_name=ev.model_name,
                response_a=ev.response_a,
                response_b=ev.response_b,
                model_a=ev.model_a,
                model_b=ev.model_b,
                judgment=ev.judgment,
                hallucination_check=ev.hallucination_check,
                comparison_result=ev.comparison_result,
                hallucination_check_a=ev.hallucination_check_a,
                hallucination_check_b=ev.hallucination_check_b,
                created_at=ev.created_at.isoformat(),
            )
            for ev in evaluations
        ],
        total=total,
    )


# User Feedback endpoints

@router.post("/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    request: FeedbackCreateRequest,
    fastapi_request: Request,
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db)
) -> FeedbackResponse:
    """Submit user feedback on an evaluation or comparison result."""
    import uuid as uuid_module

    # Get current user if available (from session)
    user = await get_user_from_session(fastapi_request, db)

    feedback = UserFeedback(
        org_id=org.id,
        user_id=user.id if user else None,
        feedback_type=request.feedback_type,
        agrees_with_result=request.agrees_with_result,
        quality_rating=request.quality_rating,
        comment=request.comment,
        saved_evaluation_id=uuid_module.UUID(request.saved_evaluation_id) if request.saved_evaluation_id else None,
        context_snapshot=request.context_snapshot,
    )

    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)

    return FeedbackResponse(
        id=str(feedback.id),
        feedback_type=feedback.feedback_type,
        agrees_with_result=feedback.agrees_with_result,
        quality_rating=feedback.quality_rating,
        comment=feedback.comment,
        saved_evaluation_id=str(feedback.saved_evaluation_id) if feedback.saved_evaluation_id else None,
        created_at=feedback.created_at.isoformat(),
    )


@router.get("/feedback", response_model=FeedbackListResponse)
async def list_feedback(
    fastapi_request: Request,
    limit: int = 20,
    offset: int = 0,
    feedback_type: str | None = None,
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db)
) -> FeedbackListResponse:
    """List user feedback for the organization."""
    query = select(UserFeedback).where(UserFeedback.org_id == org.id)

    if feedback_type:
        query = query.where(UserFeedback.feedback_type == feedback_type)

    # Count total
    count_result = await db.execute(query)
    total = len(count_result.scalars().all())

    # Get paginated results
    result = await db.execute(
        query
        .order_by(UserFeedback.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    feedback_items = result.scalars().all()

    return FeedbackListResponse(
        feedback=[
            FeedbackResponse(
                id=str(f.id),
                feedback_type=f.feedback_type,
                agrees_with_result=f.agrees_with_result,
                quality_rating=f.quality_rating,
                comment=f.comment,
                saved_evaluation_id=str(f.saved_evaluation_id) if f.saved_evaluation_id else None,
                created_at=f.created_at.isoformat(),
            )
            for f in feedback_items
        ],
        total=total,
    )


@router.get("/feedback/{feedback_id}", response_model=FeedbackResponse)
async def get_feedback(
    feedback_id: str,
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db)
) -> FeedbackResponse:
    """Get a specific feedback item."""
    result = await db.execute(
        select(UserFeedback)
        .where(UserFeedback.id == feedback_id)
        .where(UserFeedback.org_id == org.id)
    )
    feedback = result.scalar_one_or_none()

    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feedback not found: {feedback_id}"
        )

    return FeedbackResponse(
        id=str(feedback.id),
        feedback_type=feedback.feedback_type,
        agrees_with_result=feedback.agrees_with_result,
        quality_rating=feedback.quality_rating,
        comment=feedback.comment,
        saved_evaluation_id=str(feedback.saved_evaluation_id) if feedback.saved_evaluation_id else None,
        created_at=feedback.created_at.isoformat(),
    )
