"""
Prompt Optimizer Agent - Analyzes and optimizes prompts using best practices.

Uses the Judge agent to score prompts and applies prompt engineering
best practices to generate improved versions.
"""

import json
import re
import asyncio
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Literal

import llm.client as llm_client
from .judge import Judge
from .web_researcher import WebResearcher, WebSource, WebResearchResult


class OptimizerError(Exception):
    pass


ANALYZER_SYSTEM_PROMPT = """You are an expert prompt engineer analyzing prompts against 2025 best practices from OpenAI, Anthropic, and Google DeepMind.

Analyze the given prompt template and identify issues in these categories:

1. **Clarity**: Is the task clearly defined? Are instructions unambiguous and direct?
   - (From OpenAI GPT-5): Avoid "poorly-constructed prompts containing contradictory or vague instructions"

2. **Structure**: Is the prompt well-organized with consistent delimiters (XML tags or markdown)?
   - (From Google Gemini): Use consistent delimiters like <context>, <task> or markdown headings

3. **Specificity**: Are requirements explicit? Are edge cases handled?
   - (From Anthropic): Specificity means structuring instructions with explicit guidelines

4. **Output Format**: Is the expected output format clearly specified with verbosity guidance?
   - (From OpenAI): Control output verbosity explicitly. Specify response format.

5. **Role Definition**: Is there a clear persona/role with specific expertise?
   - (From Anthropic): The more specific about what you want, the better.

6. **Constraints**: Are boundaries and limitations clearly stated? Are there escape hatches?
   - (From OpenAI GPT-5): Provide escape hatches and explicit permission to proceed under uncertainty.

7. **Examples**: Would few-shot examples improve performance?
   - (From Google): "Prompts without few-shot examples are likely to be less effective."
   - IMPORTANT: If the prompt lacks concrete input/output examples and the task involves:
     * Complex formatting requirements
     * Domain-specific output structures
     * Multi-step reasoning
     * Specific writing styles or tones
   Then flag this as a HIGH severity issue with category "examples"

8. **Reasoning**: Does the prompt include chain-of-thought or step-by-step guidance for complex tasks?
   - (From Anthropic): "Think step by step" or <thinking> tags significantly improve performance.

IMPORTANT: Be thorough in identifying issues. Most prompts can benefit from few-shot examples -
if the prompt doesn't have them and the task is non-trivial, always include an "examples" issue.

Return ONLY a JSON object:

{
  "issues": [
    {"category": "clarity|structure|specificity|output_format|role|constraints|examples|reasoning",
     "description": "what's wrong",
     "severity": "high|medium|low"}
  ],
  "strengths": ["what the prompt does well"],
  "overall_quality": "poor|fair|good|excellent",
  "priority_improvements": ["top 3 things to fix first"]
}
"""

OPTIMIZER_SYSTEM_PROMPT = """<role>
You are an expert prompt engineer specializing in optimizing prompts according to 2025 best practices from OpenAI, Anthropic, and Google DeepMind.
</role>

<context>
You will receive a prompt that needs optimization, along with an analysis of its issues and optionally researched few-shot examples to incorporate.
</context>

<task>
Generate an optimized version of the prompt that addresses all identified issues while preserving the original intent.

Apply these evidence-based prompt engineering principles:

1. **Clear Role Definition** (Anthropic)
   - Start with a specific persona with defined expertise
   - Use format: "You are a [specific role] specializing in [domain]"

2. **Structured Sections** (Google Gemini)
   - Organize using consistent XML tags: <context>, <task>, <format>, <constraints>, <examples>
   - OR use consistent markdown headings (## Context, ## Task, etc.)
   - Never mix delimiters - choose one format

3. **Direct Instructions** (OpenAI GPT-5)
   - Be precise and direct - avoid vague or contradictory instructions
   - State goals clearly without unnecessary persuasive language
   - Place critical instructions at the beginning

4. **Output Format Specification** (OpenAI)
   - Explicitly specify format: JSON, markdown, bullets, tables
   - Include verbosity guidance (concise vs. detailed)
   - Provide structure templates when helpful

5. **Few-Shot Examples** (Google)
   - Include 2-4 diverse examples when provided
   - Use consistent format: Input → Output
   - Show edge cases and varying complexity

6. **Constraints & Boundaries** (OpenAI GPT-5)
   - Define what's in and out of scope
   - Include "do NOT" instructions for common failure modes
   - Add escape hatches: "If uncertain, state your assumptions"

7. **Reasoning Guidance** (Anthropic)
   - For complex tasks, add: "Think through this step by step"
   - Or use <thinking></thinking> tags for internal reasoning
</task>

<format>
Return ONLY a valid JSON object with this exact structure:

{
  "optimized_prompt": "the full optimized prompt text using XML tags or consistent markdown",
  "improvements": ["specific change 1", "specific change 2", "..."],
  "reasoning": "2-4 sentences explaining why these changes will improve performance based on the research"
}
</format>

<constraints>
- Preserve the original intent and core requirements
- Do NOT add unnecessary complexity or over-engineer
- Do NOT invent requirements not present in the original
- If few-shot examples are provided, you MUST incorporate them
- The optimized prompt should be self-contained and complete
</constraints>"""

PROMPT_SCORER_SYSTEM_PROMPT = """You are a HARSH and CRITICAL prompt engineering expert evaluating prompt quality against 2025 best practices from OpenAI, Anthropic, and Google DeepMind.

## CRITICAL SCORING PHILOSOPHY

You are deliberately harsh. Most prompts in the wild are poorly written and should score LOW (under 40/100).
- A score of 70+ should be RARE and only for prompts that follow ALL best practices
- A score of 50-70 means "acceptable but needs significant work"
- A score under 50 means "needs major improvements" (this should be MOST prompts)
- Do NOT give points for "trying" - only for actually implementing best practices correctly

Be skeptical. If something is missing, score it as 0 in that category. Partial credit should be rare.

## Scoring Rubric (100 points total)

### 1. Clarity & Specificity (0-20 points)
- **18-20**: EXCEPTIONAL - Crystal clear task, zero ambiguity, precise action verbs, explicit success criteria
- **12-17**: GOOD - Clear but missing some explicit requirements or success criteria
- **6-11**: MEDIOCRE - Understandable intent but vague execution details, uses words like "good" or "appropriate"
- **1-5**: POOR - Ambiguous, could be interpreted multiple ways
- **0**: FAILING - Confusing, contradictory, or incomprehensible

HARSH STANDARD: If the prompt uses vague words like "good", "appropriate", "relevant", "proper" without defining them = max 10 points.

### 2. Structure & Organization (0-20 points)
- **18-20**: EXCEPTIONAL - Consistent XML tags OR markdown throughout, logical section flow, clear hierarchy
- **12-17**: GOOD - Has structure but inconsistent delimiters or missing sections
- **6-11**: MEDIOCRE - Some organization but no consistent delimiter system
- **1-5**: POOR - Minimal structure, wall of text with occasional formatting
- **0**: FAILING - No structure whatsoever

HARSH STANDARD: If no XML tags AND no consistent markdown headers = max 8 points. Mixing delimiters = max 12 points.

### 3. Role Definition (0-15 points)
- **13-15**: EXCEPTIONAL - Specific expert persona with domain expertise AND behavioral guidelines
- **9-12**: GOOD - Role defined with some specificity but missing behavioral context
- **5-8**: MEDIOCRE - Generic role like "helpful assistant" or "expert"
- **1-4**: POOR - Vague role implication without explicit definition
- **0**: FAILING - No role definition at all

HARSH STANDARD: "You are a helpful assistant" = 3 points max. Must specify DOMAIN expertise for 9+ points.

### 4. Output Format Specification (0-15 points)
- **13-15**: EXCEPTIONAL - Explicit format (JSON schema, markdown template), length constraints, verbosity level
- **9-12**: GOOD - Format specified but missing length or verbosity guidance
- **5-8**: MEDIOCRE - Vague format hints like "be concise" or "use bullets"
- **1-4**: POOR - Implies format without specifying
- **0**: FAILING - No output format guidance

HARSH STANDARD: No explicit format = 0 points. "Be concise" without word/length limit = max 6 points.

### 5. Few-Shot Examples (0-15 points)
- **13-15**: EXCEPTIONAL - 2-4 diverse examples showing input→output with consistent format
- **9-12**: GOOD - Examples present but lack diversity or edge cases
- **5-8**: MEDIOCRE - Single example or examples without clear input/output structure
- **1-4**: POOR - Partial or malformed examples
- **0**: FAILING - No examples when task complexity warrants them

HARSH STANDARD: No examples for ANY non-trivial task = 0 points. This is non-negotiable per Google's research.

### 6. Constraints & Boundaries (0-10 points)
- **9-10**: EXCEPTIONAL - Explicit scope limits, "do NOT" instructions, edge case handling, escape hatches
- **6-8**: GOOD - Some constraints but missing negative instructions or edge cases
- **3-5**: MEDIOCRE - Minimal boundaries, mostly implicit
- **1-2**: POOR - Vague limitations
- **0**: FAILING - Completely open-ended when task needs boundaries

HARSH STANDARD: No "do NOT" instructions = max 6 points. No edge case handling = max 7 points.

### 7. Reasoning Guidance (0-5 points)
- **5**: EXCEPTIONAL - Explicit CoT instruction ("think step by step") OR thinking tags, multi-step breakdown
- **3-4**: GOOD - Some reasoning structure but not explicit CoT
- **1-2**: MEDIOCRE - Implies reasoning without instructing it
- **0**: FAILING - No reasoning guidance for complex task

HARSH STANDARD: Complex task without "think step by step" or equivalent = 0 points.

## Evaluation Instructions

1. Read the prompt with a CRITICAL eye - look for what's MISSING
2. Apply the HARSH STANDARDS strictly - do not give benefit of the doubt
3. Score each category independently using the strict criteria above
4. Most prompts should score 25-45 total - scores above 60 should be uncommon
5. List ALL violations and missing elements

Return ONLY a JSON object:

{
  "scores": {
    "clarity_specificity": <0-20>,
    "structure_organization": <0-20>,
    "role_definition": <0-15>,
    "output_format": <0-15>,
    "few_shot_examples": <0-15>,
    "constraints_boundaries": <0-10>,
    "reasoning_guidance": <0-5>
  },
  "total_score": <0-100>,
  "normalized_score": <0.0-10.0>,
  "weakest_areas": ["area1", "area2", "area3"],
  "best_practice_violations": ["specific violation 1", "specific violation 2", "specific violation 3"],
  "improvement_suggestions": ["specific actionable suggestion 1", "specific actionable suggestion 2"],
  "rationale": "<2-4 sentences being BLUNT about the prompt's shortcomings>"
}
"""

FEW_SHOT_RESEARCHER_PROMPT = """<role>
You are an expert prompt engineer specializing in few-shot learning and example design, applying 2025 best practices from Google DeepMind and Anthropic.
</role>

<context>
Few-shot examples are critical for prompt performance. According to Google's research: "Prompts without few-shot examples are likely to be less effective." Your task is to research and create high-quality examples that teach the model the desired behavior.
</context>

<task>
Generate 2-4 high-quality few-shot examples for the given prompt.

Follow these evidence-based guidelines:

1. **Diversity** (Google Gemini)
   - Cover different scenarios: easy, medium, and edge cases
   - Include variations the model might encounter
   - Avoid repetitive or too-similar examples

2. **Format Consistency** (Google)
   - Use identical structure for all examples
   - One primary objective is demonstrating response format
   - Choose clear delimiters: "Input:" / "Output:" or "Q:" / "A:"

3. **Progressive Complexity** (Anthropic)
   - Start with a straightforward example
   - Include at least one complex or nuanced case
   - Show how to handle ambiguity if relevant

4. **Quality Demonstration**
   - Each output should be the ideal response
   - Match the expected length, tone, and detail level
   - Show correct formatting (JSON, markdown, etc.)

5. **Pattern Teaching**
   - Examples should implicitly teach desired behaviors
   - Avoid anti-patterns - show what TO do, not what NOT to do
   - Make the underlying pattern discoverable
</task>

<format>
Return ONLY a valid JSON object:

{
  "examples": [
    {
      "input": "the example user input or query",
      "output": "the ideal response demonstrating expected format and quality",
      "rationale": "why this example teaches an important pattern"
    }
  ],
  "example_format_recommendation": "Recommended format string (e.g., 'Input: {input}\\nOutput: {output}')",
  "research_notes": "2-3 sentences on what patterns these examples collectively teach"
}
</format>

<constraints>
- Generate exactly 2-4 examples (not more, not fewer)
- Examples must be realistic and domain-appropriate
- Outputs should be complete, not truncated with "..."
- Do NOT include examples that contradict each other
- Keep individual examples concise but complete
</constraints>"""


@dataclass
class PromptScore:
    """Detailed scoring of a prompt against best practices."""
    scores: Dict[str, int] = field(default_factory=dict)
    total_score: int = 0
    normalized_score: float = 0.0
    weakest_areas: List[str] = field(default_factory=list)
    best_practice_violations: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)
    rationale: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scores": self.scores,
            "total_score": self.total_score,
            "normalized_score": self.normalized_score,
            "weakest_areas": self.weakest_areas,
            "best_practice_violations": self.best_practice_violations,
            "improvement_suggestions": self.improvement_suggestions,
            "rationale": self.rationale
        }


@dataclass
class FewShotExample:
    """A single few-shot example."""
    input: str
    output: str
    rationale: str = ""


@dataclass
class FewShotResearch:
    """Research results for few-shot examples."""
    examples: List[FewShotExample] = field(default_factory=list)
    format_recommendation: str = ""
    research_notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "examples": [{"input": e.input, "output": e.output, "rationale": e.rationale} for e in self.examples],
            "format_recommendation": self.format_recommendation,
            "research_notes": self.research_notes
        }

    def format_for_prompt(self) -> str:
        """Format examples for inclusion in a prompt."""
        if not self.examples:
            return ""

        formatted = []
        for i, ex in enumerate(self.examples, 1):
            formatted.append(f"Example {i}:\nInput: {ex.input}\nOutput: {ex.output}")

        return "\n\n".join(formatted)


@dataclass
class PromptAnalysis:
    """Analysis of a prompt's quality and issues."""
    issues: List[Dict[str, str]] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    overall_quality: str = "fair"
    priority_improvements: List[str] = field(default_factory=list)

    def needs_few_shot_examples(self) -> bool:
        """Check if analysis identified a need for few-shot examples."""
        for issue in self.issues:
            if issue.get("category") == "examples":
                return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "issues": self.issues,
            "strengths": self.strengths,
            "overall_quality": self.overall_quality,
            "priority_improvements": self.priority_improvements
        }


@dataclass
class OptimizationResult:
    """Result of prompt optimization."""
    original_prompt: str
    optimized_prompt: str
    original_score: float
    optimized_score: float
    improvements: List[str] = field(default_factory=list)
    reasoning: str = ""
    analysis: Optional[PromptAnalysis] = None
    few_shot_research: Optional[FewShotResearch] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_prompt": self.original_prompt,
            "optimized_prompt": self.optimized_prompt,
            "original_score": self.original_score,
            "optimized_score": self.optimized_score,
            "improvements": self.improvements,
            "reasoning": self.reasoning,
            "analysis": self.analysis.to_dict() if self.analysis else None,
            "few_shot_research": self.few_shot_research.to_dict() if self.few_shot_research else None
        }


@dataclass
class JudgeEvaluation:
    """Evaluation result from the Judge agent."""
    judge_score: float
    is_improvement: bool
    improvement_margin: Optional[str] = None  # "slightly", "moderately", "strongly"
    tags: List[str] = field(default_factory=list)
    rationale: str = ""
    has_regressions: bool = False
    regression_details: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "judge_score": self.judge_score,
            "is_improvement": self.is_improvement,
            "improvement_margin": self.improvement_margin,
            "tags": self.tags,
            "rationale": self.rationale,
            "has_regressions": self.has_regressions,
            "regression_details": self.regression_details
        }


@dataclass
class EnhancedOptimizationResult:
    """Result of enhanced prompt optimization with web research and judge evaluation."""
    original_prompt: str
    optimized_prompt: str
    original_score: float
    optimized_score: float
    improvements: List[str] = field(default_factory=list)
    reasoning: str = ""
    analysis: Optional[PromptAnalysis] = None
    few_shot_research: Optional[FewShotResearch] = None
    # Enhanced fields
    mode: str = "enhanced"
    web_sources: List[WebSource] = field(default_factory=list)
    judge_evaluation: Optional[JudgeEvaluation] = None
    iterations_used: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_prompt": self.original_prompt,
            "optimized_prompt": self.optimized_prompt,
            "original_score": self.original_score,
            "optimized_score": self.optimized_score,
            "improvements": self.improvements,
            "reasoning": self.reasoning,
            "analysis": self.analysis.to_dict() if self.analysis else None,
            "few_shot_research": self.few_shot_research.to_dict() if self.few_shot_research else None,
            "mode": self.mode,
            "web_sources": [{"url": s.url, "title": s.title, "content": s.content} for s in self.web_sources],
            "judge_evaluation": self.judge_evaluation.to_dict() if self.judge_evaluation else None,
            "iterations_used": self.iterations_used
        }


class PromptOptimizer:
    """
    Optimizes prompts using Judge evaluation and prompt engineering best practices.

    Usage:
        optimizer = PromptOptimizer()
        result = optimizer.optimize(
            prompt_template="You are a helpful assistant...",
            task_description="Answer user questions about Python",
            sample_inputs=["How do I read a file?", "What is a list comprehension?"]
        )
        print(f"Score improved from {result.original_score} to {result.optimized_score}")
        print(result.optimized_prompt)
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.judge = Judge(model="gpt-4o-mini")

    def analyze(self, prompt_template: str, task_description: str) -> PromptAnalysis:
        """
        Analyze a prompt template and identify optimization opportunities.

        Args:
            prompt_template: The prompt to analyze
            task_description: What the prompt is supposed to accomplish

        Returns:
            PromptAnalysis with issues, strengths, and priority improvements
        """
        user_content = f"""Task Description: {task_description}

Prompt Template to Analyze:
---
{prompt_template}
---

Analyze this prompt for optimization opportunities."""

        messages = [
            {"role": "system", "content": ANALYZER_SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ]

        response_text = llm_client.chat(self.model, messages)
        return self._parse_analysis(response_text)

    def optimize(
        self,
        prompt_template: str,
        task_description: str,
        sample_inputs: Optional[List[str]] = None
    ) -> OptimizationResult:
        """
        Optimize a prompt template using analysis and best practices.

        Args:
            prompt_template: The prompt to optimize
            task_description: What the prompt is supposed to accomplish
            sample_inputs: Optional sample inputs to test the prompt

        Returns:
            OptimizationResult with original and optimized prompts, scores, and improvements
        """
        # Step 1: Analyze the original prompt
        analysis = self.analyze(prompt_template, task_description)

        # Step 2: Research few-shot examples if needed
        few_shot_research = None
        if analysis.needs_few_shot_examples():
            few_shot_research = self.research_few_shot_examples(
                prompt_template,
                task_description
            )

        # Step 3: Score the original prompt
        original_score = self._score_prompt(
            prompt_template,
            task_description,
            sample_inputs or ["Provide a general response"]
        )

        # Step 4: Generate optimized version (with few-shot examples if researched)
        optimized_prompt, improvements, reasoning = self._generate_optimized(
            prompt_template,
            task_description,
            analysis,
            few_shot_research
        )

        # Step 5: Score the optimized prompt
        optimized_score = self._score_prompt(
            optimized_prompt,
            task_description,
            sample_inputs or ["Provide a general response"]
        )

        return OptimizationResult(
            original_prompt=prompt_template,
            optimized_prompt=optimized_prompt,
            original_score=original_score,
            optimized_score=optimized_score,
            improvements=improvements,
            reasoning=reasoning,
            analysis=analysis,
            few_shot_research=few_shot_research
        )

    def research_few_shot_examples(
        self,
        prompt_template: str,
        task_description: str
    ) -> FewShotResearch:
        """
        Research and generate high-quality few-shot examples for a prompt.

        Args:
            prompt_template: The prompt that needs examples
            task_description: What the prompt is supposed to accomplish

        Returns:
            FewShotResearch with examples and formatting recommendations
        """
        user_content = f"""Task Description: {task_description}

Original Prompt:
---
{prompt_template}
---

Research and create 2-4 high-quality few-shot examples that would help this prompt perform better.
Consider:
1. What are typical inputs this prompt would receive?
2. What does an ideal output look like?
3. What edge cases or variations should be covered?
4. What format would make the examples clearest?"""

        messages = [
            {"role": "system", "content": FEW_SHOT_RESEARCHER_PROMPT},
            {"role": "user", "content": user_content}
        ]

        response_text = llm_client.chat(self.model, messages)
        return self._parse_few_shot_research(response_text)

    def _parse_few_shot_research(self, response: str) -> FewShotResearch:
        """Parse the few-shot research response from the LLM."""
        try:
            json_match = re.search(r"\{[\s\S]*\}", response)
            if not json_match:
                return FewShotResearch()

            data = json.loads(json_match.group())

            examples = []
            for ex in data.get("examples", []):
                examples.append(FewShotExample(
                    input=ex.get("input", ""),
                    output=ex.get("output", ""),
                    rationale=ex.get("rationale", "")
                ))

            return FewShotResearch(
                examples=examples,
                format_recommendation=data.get("example_format_recommendation", ""),
                research_notes=data.get("research_notes", "")
            )
        except json.JSONDecodeError:
            return FewShotResearch()

    def _score_prompt(
        self,
        prompt_template: str,
        task_description: str,
        sample_inputs: List[str]
    ) -> float:
        """
        Score a prompt against 2025 best practices from OpenAI, Anthropic, and Google.

        Uses a comprehensive rubric based on latest AI lab research to evaluate:
        - Clarity & Specificity (0-20)
        - Structure & Organization (0-20)
        - Role Definition (0-15)
        - Output Format Specification (0-15)
        - Few-Shot Examples (0-15)
        - Constraints & Boundaries (0-10)
        - Reasoning Guidance (0-5)

        Returns a normalized score from 0-10.
        """
        score_result = self.score_prompt_detailed(prompt_template, task_description)
        return score_result.normalized_score

    def score_prompt_detailed(
        self,
        prompt_template: str,
        task_description: str
    ) -> PromptScore:
        """
        Get detailed scoring breakdown for a prompt.

        Returns PromptScore with category scores, violations, and suggestions.
        """
        user_content = f"""Task Description: {task_description}

Prompt Template to Score:
---
{prompt_template}
---

Evaluate this prompt against modern prompt engineering best practices."""

        messages = [
            {"role": "system", "content": PROMPT_SCORER_SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ]

        try:
            response_text = llm_client.chat(self.model, messages)
            return self._parse_score_response(response_text)
        except Exception:
            # Return default middle score on error
            return PromptScore(
                scores={},
                total_score=50,
                normalized_score=5.0,
                rationale="Scoring failed - using default"
            )

    def _parse_score_response(self, response: str) -> PromptScore:
        """Parse the scoring response from the LLM."""
        try:
            json_match = re.search(r"\{[\s\S]*\}", response)
            if not json_match:
                return PromptScore(
                    total_score=50,
                    normalized_score=5.0,
                    rationale="Failed to parse scoring response"
                )

            data = json.loads(json_match.group())

            return PromptScore(
                scores=data.get("scores", {}),
                total_score=data.get("total_score", 50),
                normalized_score=data.get("normalized_score", 5.0),
                weakest_areas=data.get("weakest_areas", []),
                best_practice_violations=data.get("best_practice_violations", []),
                improvement_suggestions=data.get("improvement_suggestions", []),
                rationale=data.get("rationale", "")
            )
        except json.JSONDecodeError:
            return PromptScore(
                total_score=50,
                normalized_score=5.0,
                rationale="Failed to parse scoring JSON"
            )

    def _render_prompt(self, template: str, user_input: str) -> str:
        """Render a prompt template with user input."""
        # Support common template patterns
        rendered = template
        rendered = rendered.replace("{{input}}", user_input)
        rendered = rendered.replace("{{user_input}}", user_input)
        rendered = rendered.replace("{input}", user_input)
        rendered = rendered.replace("{user_input}", user_input)

        # If no template variable found, append input
        if user_input not in rendered and "{{" not in template and "{" not in template:
            rendered = f"{template}\n\nUser Input: {user_input}"

        return rendered

    def _generate_optimized(
        self,
        prompt_template: str,
        task_description: str,
        analysis: PromptAnalysis,
        few_shot_research: Optional[FewShotResearch] = None
    ) -> tuple[str, List[str], str]:
        """Generate an optimized version of the prompt."""
        # Build the few-shot examples section if research was done
        few_shot_section = ""
        if few_shot_research and few_shot_research.examples:
            examples_formatted = []
            for i, ex in enumerate(few_shot_research.examples, 1):
                examples_formatted.append(
                    f"Example {i}:\n"
                    f"  Input: {ex.input}\n"
                    f"  Output: {ex.output}\n"
                    f"  (Rationale: {ex.rationale})"
                )
            few_shot_section = f"""

Researched Few-Shot Examples to Include:
{chr(10).join(examples_formatted)}

Format Recommendation: {few_shot_research.format_recommendation}
Research Notes: {few_shot_research.research_notes}

IMPORTANT: Incorporate these few-shot examples into the optimized prompt in a clear "Examples" section.
The examples should demonstrate the expected input/output format and quality."""

        user_content = f"""Task Description: {task_description}

Original Prompt:
---
{prompt_template}
---

Analysis of Issues:
{json.dumps(analysis.to_dict(), indent=2)}
{few_shot_section}

Generate an optimized version of this prompt that addresses the identified issues."""

        messages = [
            {"role": "system", "content": OPTIMIZER_SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ]

        response_text = llm_client.chat(self.model, messages)
        return self._parse_optimization(response_text, prompt_template)

    def _parse_analysis(self, response: str) -> PromptAnalysis:
        """Parse the analysis response from the LLM."""
        try:
            json_match = re.search(r"\{[\s\S]*\}", response)
            if not json_match:
                raise OptimizerError(f"No JSON found in analysis response")

            data = json.loads(json_match.group())

            return PromptAnalysis(
                issues=data.get("issues", []),
                strengths=data.get("strengths", []),
                overall_quality=data.get("overall_quality", "fair"),
                priority_improvements=data.get("priority_improvements", [])
            )
        except json.JSONDecodeError as e:
            raise OptimizerError(f"Failed to parse analysis JSON: {e}")

    def _parse_optimization(
        self,
        response: str,
        fallback_prompt: str
    ) -> tuple[str, List[str], str]:
        """Parse the optimization response from the LLM."""
        try:
            json_match = re.search(r"\{[\s\S]*\}", response)
            if not json_match:
                raise OptimizerError(f"No JSON found in optimization response")

            data = json.loads(json_match.group())

            optimized = data.get("optimized_prompt", fallback_prompt)
            improvements = data.get("improvements", [])
            reasoning = data.get("reasoning", "")

            return optimized, improvements, reasoning
        except json.JSONDecodeError as e:
            # Return original if parsing fails
            return fallback_prompt, [], f"Parsing failed: {e}"

    async def optimize_enhanced(
        self,
        prompt_template: str,
        task_description: str,
        sample_inputs: Optional[List[str]] = None
    ) -> EnhancedOptimizationResult:
        """
        Enhanced optimization with web-researched examples and Judge evaluation.

        This method is intended for paid tiers and provides:
        - Web search for real-world few-shot examples (via Tavily)
        - Judge evaluation to verify improvement quality
        - Single retry if regression is detected

        Args:
            prompt_template: The prompt to optimize
            task_description: What the prompt should accomplish
            sample_inputs: Optional sample inputs for testing

        Returns:
            EnhancedOptimizationResult with web sources and judge evaluation
        """
        web_sources: List[WebSource] = []
        iterations_used = 1

        # Step 1: Analyze the original prompt
        analysis = self.analyze(prompt_template, task_description)

        # Step 2: Research few-shot examples using web search
        few_shot_research = None
        web_research_result = None

        if analysis.needs_few_shot_examples():
            web_researcher = WebResearcher(model=self.model)

            if web_researcher.is_available:
                # Use web search for examples
                web_research_result = await web_researcher.research_examples(
                    prompt_template,
                    task_description
                )
                web_sources = web_research_result.sources

                # Convert web research to FewShotResearch format
                if web_research_result.examples:
                    few_shot_research = FewShotResearch(
                        examples=[
                            FewShotExample(
                                input=ex.get("input", ""),
                                output=ex.get("output", ""),
                                rationale=ex.get("rationale", "")
                            )
                            for ex in web_research_result.examples
                        ],
                        format_recommendation="Input: {input}\nOutput: {output}",
                        research_notes=web_research_result.research_notes
                    )

            # Fallback to LLM-generated examples if web search unavailable or failed
            if not few_shot_research:
                few_shot_research = self.research_few_shot_examples(
                    prompt_template,
                    task_description
                )

        # Step 3: Score the original prompt
        original_score = self._score_prompt(
            prompt_template,
            task_description,
            sample_inputs or ["Provide a general response"]
        )

        # Step 4: Generate optimized version
        optimized_prompt, improvements, reasoning = self._generate_optimized(
            prompt_template,
            task_description,
            analysis,
            few_shot_research
        )

        # Step 5: Score the optimized prompt
        optimized_score = self._score_prompt(
            optimized_prompt,
            task_description,
            sample_inputs or ["Provide a general response"]
        )

        # Step 6: Judge evaluation - verify improvement quality
        judge_evaluation = self._evaluate_with_judge(
            prompt_template,
            optimized_prompt,
            task_description
        )

        # Step 7: Retry if regression detected
        if judge_evaluation.has_regressions and not judge_evaluation.is_improvement:
            iterations_used = 2

            # Re-optimize with feedback about regressions
            retry_feedback = f"""
Previous optimization attempt caused regressions:
{judge_evaluation.regression_details}

Original rationale: {judge_evaluation.rationale}

Please create a new optimization that:
1. Addresses the original issues identified in the analysis
2. Does NOT introduce the regressions mentioned above
3. Preserves the strengths of the original prompt
"""
            # Add regression feedback to analysis
            analysis_with_feedback = PromptAnalysis(
                issues=analysis.issues + [{"category": "regression", "description": judge_evaluation.regression_details, "severity": "high"}],
                strengths=analysis.strengths,
                overall_quality=analysis.overall_quality,
                priority_improvements=[retry_feedback] + analysis.priority_improvements
            )

            # Retry optimization
            optimized_prompt, improvements, reasoning = self._generate_optimized(
                prompt_template,
                task_description,
                analysis_with_feedback,
                few_shot_research
            )

            # Re-score
            optimized_score = self._score_prompt(
                optimized_prompt,
                task_description,
                sample_inputs or ["Provide a general response"]
            )

            # Re-evaluate with Judge
            judge_evaluation = self._evaluate_with_judge(
                prompt_template,
                optimized_prompt,
                task_description
            )

        return EnhancedOptimizationResult(
            original_prompt=prompt_template,
            optimized_prompt=optimized_prompt,
            original_score=original_score,
            optimized_score=optimized_score,
            improvements=improvements,
            reasoning=reasoning,
            analysis=analysis,
            few_shot_research=few_shot_research,
            mode="enhanced",
            web_sources=web_sources,
            judge_evaluation=judge_evaluation,
            iterations_used=iterations_used
        )

    def _evaluate_with_judge(
        self,
        original_prompt: str,
        optimized_prompt: str,
        task_description: str
    ) -> JudgeEvaluation:
        """
        Use Judge agent to evaluate the optimization quality.

        Performs pairwise comparison and checks for regressions.
        """
        # Use pairwise comparison to determine if optimized is better
        try:
            comparison = self.judge.evaluate_pairwise(
                task_description=f"Evaluate prompt quality for: {task_description}",
                user_input="Which prompt template is more effective and follows best practices?",
                output_a=original_prompt,
                output_b=optimized_prompt
            )

            is_improvement = comparison.get("winner") == "B"
            margin = comparison.get("margin", "slightly")
            tags = comparison.get("tags", [])
            rationale = comparison.get("rationale", "")

            # Check for regression indicators
            regression_tags = ["missing_key_detail", "less_clear", "lost_functionality", "worse_structure"]
            detected_regressions = [t for t in tags if any(r in t.lower() for r in regression_tags)]
            has_regressions = len(detected_regressions) > 0 or (not is_improvement and margin in ["moderately", "strongly"])

            regression_details = ""
            if has_regressions:
                if detected_regressions:
                    regression_details = f"Detected issues: {', '.join(detected_regressions)}. "
                if not is_improvement:
                    regression_details += f"Original prompt was {margin} better. {rationale}"

            return JudgeEvaluation(
                judge_score=8.0 if is_improvement else 5.0,  # Simplified score
                is_improvement=is_improvement,
                improvement_margin=margin if is_improvement else None,
                tags=tags,
                rationale=rationale,
                has_regressions=has_regressions,
                regression_details=regression_details
            )

        except Exception as e:
            # Fallback if Judge evaluation fails
            return JudgeEvaluation(
                judge_score=0.0,
                is_improvement=True,  # Assume improvement if we can't evaluate
                rationale=f"Judge evaluation failed: {str(e)}",
                has_regressions=False
            )
