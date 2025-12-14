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


ANALYZER_SYSTEM_PROMPT = """You are an expert prompt engineer analyzing prompts for optimization opportunities.

Analyze the given prompt template and identify issues in these categories:

1. **Clarity**: Is the task clearly defined? Are instructions unambiguous?
2. **Structure**: Is the prompt well-organized with clear sections?
3. **Specificity**: Are requirements explicit? Are edge cases handled?
4. **Output Format**: Is the expected output format clearly specified?
5. **Role Definition**: Is there a clear persona/role for the AI?
6. **Constraints**: Are boundaries and limitations clearly stated?
7. **Examples**: Would few-shot examples improve performance?

Return ONLY a JSON object:

{
  "issues": [
    {"category": "clarity|structure|specificity|output_format|role|constraints|examples",
     "description": "what's wrong",
     "severity": "high|medium|low"}
  ],
  "strengths": ["what the prompt does well"],
  "overall_quality": "poor|fair|good|excellent",
  "priority_improvements": ["top 3 things to fix first"]
}
"""

OPTIMIZER_SYSTEM_PROMPT = """You are an expert prompt engineer. Your task is to optimize prompts using industry best practices.

Apply these prompt engineering principles:

1. **Clear Role Definition**: Start with a clear persona/role for the AI
2. **Structured Sections**: Organize into Context, Task, Format, Constraints
3. **Explicit Instructions**: Be specific about what to do and what NOT to do
4. **Output Format**: Clearly specify the expected response format
5. **Chain of Thought**: Add reasoning instructions when beneficial
6. **Edge Case Handling**: Address potential ambiguous scenarios
7. **Constraints & Boundaries**: Define what's in and out of scope
8. **Examples**: Add few-shot examples if they would help

Given:
- The original prompt
- The task description
- The analysis of issues

Generate an optimized version that addresses the identified issues while preserving the original intent.

Return ONLY a JSON object:

{
  "optimized_prompt": "the full optimized prompt text",
  "improvements": ["list of specific changes made"],
  "reasoning": "2-4 sentences explaining why these changes will improve performance"
}
"""


@dataclass
class PromptAnalysis:
    """Analysis of a prompt's quality and issues."""
    issues: List[Dict[str, str]] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    overall_quality: str = "fair"
    priority_improvements: List[str] = field(default_factory=list)

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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_prompt": self.original_prompt,
            "optimized_prompt": self.optimized_prompt,
            "original_score": self.original_score,
            "optimized_score": self.optimized_score,
            "improvements": self.improvements,
            "reasoning": self.reasoning,
            "analysis": self.analysis.to_dict() if self.analysis else None
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

    def __init__(self, model: str = "gpt-4o"):
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

        # Step 2: Score the original prompt
        original_score = self._score_prompt(
            prompt_template,
            task_description,
            sample_inputs or ["Provide a general response"]
        )

        # Step 3: Generate optimized version
        optimized_prompt, improvements, reasoning = self._generate_optimized(
            prompt_template,
            task_description,
            analysis
        )

        # Step 4: Score the optimized prompt
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
            analysis=analysis
        )

    def _score_prompt(
        self,
        prompt_template: str,
        task_description: str,
        sample_inputs: List[str]
    ) -> float:
        """
        Score a prompt by running it against sample inputs and averaging Judge scores.
        """
        if not sample_inputs:
            return 5.0  # Default middle score if no samples

        scores = []
        for sample_input in sample_inputs[:3]:  # Limit to 3 samples for efficiency
            # Generate a response using the prompt
            test_prompt = self._render_prompt(prompt_template, sample_input)
            messages = [{"role": "user", "content": test_prompt}]

            try:
                response = llm_client.chat("gpt-4o-mini", messages)

                # Judge the response
                eval_result = self.judge.evaluate_single(
                    task_description=task_description,
                    user_input=sample_input,
                    candidate_output=response
                )
                scores.append(eval_result.get("overall_score", 5.0))
            except Exception:
                scores.append(5.0)  # Default on error

        return sum(scores) / len(scores) if scores else 5.0

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
        analysis: PromptAnalysis
    ) -> tuple[str, List[str], str]:
        """Generate an optimized version of the prompt."""
        user_content = f"""Task Description: {task_description}

Original Prompt:
---
{prompt_template}
---

Analysis of Issues:
{json.dumps(analysis.to_dict(), indent=2)}

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
