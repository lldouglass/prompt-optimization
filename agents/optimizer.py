"""
Prompt Optimizer Agent - Analyzes and optimizes prompts using best practices.

Uses the Judge agent to score prompts and applies prompt engineering
best practices to generate improved versions.
"""

import json
import re
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

import llm.client as llm_client
from .judge import Judge


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

PROMPT_SCORER_SYSTEM_PROMPT = """You are an expert prompt engineer evaluating prompt quality against 2025 best practices from OpenAI, Anthropic, and Google DeepMind.

Score the prompt template on these criteria (based on latest AI lab research):

## Scoring Rubric (100 points total)

### 1. Clarity & Specificity (0-20 points)
- **20**: Crystal clear task definition, explicit requirements, direct language, no ambiguity
- **15**: Clear instructions with minor ambiguities
- **10**: Generally understandable but vague in places
- **5**: Unclear or overly broad instructions
- **0**: Confusing or contradictory instructions

Key factors (from OpenAI GPT-5 guide): Avoid "poorly-constructed prompts containing contradictory or vague instructions" which waste reasoning tokens. Be direct and precise.

### 2. Structure & Organization (0-20 points)
- **20**: Well-organized with clear sections, consistent delimiters (XML tags like <context>, <task> or markdown), logical flow
- **15**: Good structure with minor inconsistencies
- **10**: Some organization but inconsistent formatting
- **5**: Poorly organized, mixed formatting
- **0**: No discernible structure

Key factors (from Google Gemini guide): Use consistent delimiters, XML-style tags or Markdown headings. Choose one format and use it consistently.

### 3. Role Definition (0-15 points)
- **15**: Clear persona with specific expertise, appropriate context for behavior
- **10**: Role defined but lacks specificity
- **5**: Vague role or generic assistant framing
- **0**: No role definition

Key factors (from Anthropic): Specificity means structuring instructions with explicit guidelines. The more specific about what you want, the better.

### 4. Output Format Specification (0-15 points)
- **15**: Explicit format requirements, examples of structure, verbosity guidance
- **10**: Format specified but incomplete
- **5**: Vague format hints
- **0**: No output format specified

Key factors (from OpenAI): Control output verbosity explicitly. Specify response format (tables, JSON, bullets, length constraints).

### 5. Few-Shot Examples (0-15 points)
- **15**: 2-4 diverse, high-quality examples with consistent format
- **10**: Examples present but limited diversity or quality
- **5**: Single example or poorly formatted
- **0**: No examples (when examples would help)

Key factors (from Google): "Prompts without few-shot examples are likely to be less effective." Examples should show desired output format with consistent structure.

### 6. Constraints & Boundaries (0-10 points)
- **10**: Clear scope, edge case handling, explicit "do NOT" instructions, escape hatches
- **7**: Some constraints defined
- **3**: Minimal boundary setting
- **0**: No constraints (open-ended when shouldn't be)

Key factors (from OpenAI GPT-5): Provide "escape hatches for constraint relaxation" and explicit permission to proceed under uncertainty.

### 7. Reasoning Guidance (0-5 points)
- **5**: Explicit chain-of-thought or step-by-step instructions, thinking tags
- **3**: Some reasoning guidance
- **0**: No reasoning instructions (when complex task warrants it)

Key factors (from Anthropic): "Think step by step" or `<thinking></thinking>` tags significantly improve complex task performance.

## Evaluation Instructions

1. Read the prompt carefully
2. Score each category independently
3. Calculate total score (0-100)
4. Identify the weakest areas for improvement
5. Note any violations of modern best practices

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
  "weakest_areas": ["area1", "area2"],
  "best_practice_violations": ["violation1", "violation2"],
  "improvement_suggestions": ["suggestion1", "suggestion2"],
  "rationale": "<2-4 sentences explaining the overall assessment>"
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

    def __init__(self, model: str = "gpt-5-mini"):
        self.model = model
        self.judge = Judge(model="gpt-5-mini")

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
