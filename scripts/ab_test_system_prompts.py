"""
A/B Test System Prompts for the Optimizer Agent

This script tests different system prompt variants to find which produces
the best optimized prompts, using the Judge agent for scoring.

Usage:
    cd backend && uv run python ../scripts/ab_test_system_prompts.py
"""

import asyncio
import json
from dataclasses import dataclass, field
from typing import Optional
import os

# Add parent to path for imports
import sys
sys.path.insert(0, '.')

from agents.optimizer_agent import OptimizerAgent, AgentState, AGENT_SYSTEM_PROMPT
from agents import LegacyJudge
from llm.client import LLMClient


# Test cases - prompts to optimize
TEST_CASES = [
    {
        "name": "Simple-Creative",
        "prompt": "Write a poem about cats",
        "task": "Generate creative poetry about felines"
    },
    {
        "name": "Medium-Analytical",
        "prompt": "Summarize this article for me",
        "task": "Create concise article summaries"
    },
    {
        "name": "Complex-MultiStep",
        "prompt": "Create a customer support chatbot that handles refunds, complaints, and product questions",
        "task": "Build an AI customer service agent with multiple capabilities"
    },
    {
        "name": "Technical-Precise",
        "prompt": "Convert natural language to SQL queries",
        "task": "Translate English questions into accurate SQL statements"
    },
]


# System prompt variants to test
PROMPT_VARIANTS = {
    "current": AGENT_SYSTEM_PROMPT,

    "strict_structure": """You are an expert prompt optimization agent. Transform prompts into comprehensive, production-ready versions.

## MANDATORY: Every optimized prompt MUST contain these XML sections IN ORDER:

1. <role>
   - Expert persona: "You are a [specific title] with [X] years of experience in [domain]"
   - Behavioral guidelines: professional, thorough, etc.

2. <context>
   - Background information the AI needs
   - User's situation and goals
   - Any constraints or requirements

3. <task>
   - Clear, numbered steps
   - Explicit success criteria
   - What "done" looks like

4. <format>
   - EXACT output structure (JSON schema, markdown template, etc.)
   - Length requirements (word count, sections)
   - Verbosity level

5. <examples>
   - EXACTLY 3 diverse examples
   - Format: Input → Output
   - Include: typical case, edge case, error handling case

6. <constraints>
   - 5+ specific "DO NOT" rules
   - Edge case handling
   - Escape hatch: "If uncertain about X, ask for clarification"

## Tools
- analyze_prompt: Score 0-10, identify issues. CALL THIS FIRST.
- generate_optimized_prompt: Output the comprehensive prompt.

## CRITICAL RULES
- Output MUST be 3-5x longer than input
- Missing ANY section = failure
- Vague language ("good", "appropriate") = failure
- No examples = failure""",

    "example_heavy": """You are a prompt optimization agent specializing in few-shot learning and demonstration-based prompting.

## Your Primary Mission
Transform prompts by adding HIGH-QUALITY, DIVERSE examples that demonstrate exactly what the AI should do.

## Example Requirements (CRITICAL)
Every optimized prompt MUST include:

1. **4-6 Examples minimum** - more is better
2. **Diversity requirements:**
   - Simple/typical case
   - Complex/edge case
   - Error/invalid input case
   - Boundary condition case
   - Multi-step reasoning case (if applicable)

3. **Example format:**
   ```
   <example>
   <input>[realistic user input]</input>
   <thinking>[step-by-step reasoning - show the work]</thinking>
   <output>[ideal response]</output>
   </example>
   ```

4. **Example quality criteria:**
   - Realistic, not toy examples
   - Detailed enough to learn from
   - Show edge cases and error handling
   - Demonstrate the expected format

## Also Include
- Role definition with expertise
- Output format specification
- Key constraints and DO NOTs

## Tools
- analyze_prompt: Identify what examples would help most
- generate_optimized_prompt: Create example-rich prompt

Examples are worth 10x more than instructions. Show, don't tell.""",

    "reasoning_focused": """You are a prompt optimization agent that creates prompts enabling systematic reasoning.

## Core Philosophy
The best prompts guide AI through step-by-step thinking, not just tell it what to output.

## Every Optimized Prompt Must Include:

### 1. Reasoning Framework
Add explicit thinking structure:
```
<thinking>
1. First, I will [identify/analyze/consider]...
2. Then, I will [evaluate/compare/synthesize]...
3. Finally, I will [conclude/recommend/output]...
</thinking>
```

### 2. Chain-of-Thought Triggers
- "Think through this step by step"
- "Before answering, consider..."
- "Break this down into sub-problems"
- "What are the key factors to consider?"

### 3. Self-Verification
- "Check your reasoning for logical errors"
- "Verify your answer against the constraints"
- "If your answer seems wrong, reconsider"

### 4. Structured Sections
Use XML tags: <role>, <context>, <task>, <reasoning_steps>, <format>, <verification>

### 5. Examples with Visible Reasoning
Show the thinking process, not just input→output:
```
Input: [question]
Thinking: [step 1]... [step 2]... [step 3]...
Output: [answer]
```

## Tools
- analyze_prompt: Identify reasoning gaps
- generate_optimized_prompt: Create reasoning-enabled prompt

Make the AI's thinking visible and systematic.""",

    "constraint_focused": """You are a prompt optimization agent that prevents AI failures through comprehensive constraints.

## Philosophy
Most AI failures come from unclear boundaries. Your job is to make boundaries EXPLICIT.

## Every Optimized Prompt MUST Include:

### 1. Positive Instructions (What TO Do)
- Clear task definition
- Success criteria
- Expected output format

### 2. Negative Instructions (What NOT To Do) - CRITICAL
Include 8-12 specific constraints:
- "DO NOT make assumptions about [X]"
- "DO NOT include [Y] unless explicitly requested"
- "NEVER [dangerous action]"
- "AVOID [common mistake]"
- "If [edge case], do [safe action] instead"

### 3. Boundary Conditions
- Input validation: "If input is [invalid], respond with [error message]"
- Scope limits: "This prompt handles [X, Y, Z] only. For [A, B, C], decline politely"
- Confidence thresholds: "If confidence < 80%, state uncertainty"

### 4. Escape Hatches
- "If the request is ambiguous, ask for clarification"
- "If you cannot complete the task, explain why"
- "If the request violates guidelines, decline and explain"

### 5. Error Recovery
- "If you make a mistake, acknowledge and correct"
- "If stuck, break down into smaller steps"

### 6. Standard Sections
Role, context, examples (showing constraint handling), format

## Tools
- analyze_prompt: Find missing constraints and failure modes
- generate_optimized_prompt: Create bulletproof prompt

Constraints prevent failures. Be thorough.""",
}


@dataclass
class ScoreBreakdown:
    comprehensiveness: float = 0
    structure_quality: float = 0
    example_quality: float = 0
    actionability: float = 0
    specificity: float = 0
    overall: float = 0
    reasoning: str = ""


@dataclass
class TestResult:
    variant: str
    test_name: str
    prompt_length: int
    scores: ScoreBreakdown
    optimized_prompt: str


def score_with_heuristics(optimized_prompt: str) -> ScoreBreakdown:
    """Score an optimized prompt using heuristics (fallback if Judge unavailable)."""
    scores = ScoreBreakdown()
    text = optimized_prompt.lower()

    # Comprehensiveness (0-10): Check for required sections
    sections = ["role", "context", "task", "format", "example", "constraint"]
    sections_found = sum(1 for s in sections if s in text or f"<{s}" in text)
    scores.comprehensiveness = min(10, sections_found * 1.7)

    # Structure Quality (0-10): XML tags and organization
    xml_tags = ["<role>", "<context>", "<task>", "<format>", "<constraints>", "<examples>", "<example>"]
    xml_count = sum(1 for tag in xml_tags if tag in text)
    has_consistent_structure = xml_count >= 3 or text.count("##") >= 3
    scores.structure_quality = min(10, xml_count * 1.5 + (3 if has_consistent_structure else 0))

    # Example Quality (0-10): Look for diverse, well-formatted examples
    example_count = text.count("<example>") + text.count("example 1") + text.count("**example")
    has_input_output = "input" in text and "output" in text
    scores.example_quality = min(10, example_count * 2 + (3 if has_input_output else 0))

    # Actionability (0-10): Could use immediately?
    has_clear_task = "<task>" in text or "## task" in text
    has_format_spec = "<format>" in text or "output format" in text or "respond with" in text
    length_ok = len(optimized_prompt) > 800
    scores.actionability = (4 if has_clear_task else 0) + (3 if has_format_spec else 0) + (3 if length_ok else 0)

    # Specificity (0-10): Precise vs vague
    vague_words = ["good", "appropriate", "relevant", "proper", "suitable", "nice"]
    vague_count = sum(text.count(w) for w in vague_words)
    specific_phrases = ["must", "exactly", "always", "never", "do not", "required"]
    specific_count = sum(text.count(p) for p in specific_phrases)
    scores.specificity = min(10, max(0, 7 + specific_count - vague_count * 2))

    # Overall weighted average
    scores.overall = (
        scores.comprehensiveness * 0.25 +
        scores.structure_quality * 0.20 +
        scores.example_quality * 0.25 +
        scores.actionability * 0.15 +
        scores.specificity * 0.15
    )

    scores.reasoning = f"Sections:{sections_found}/6, XML:{xml_count}, Examples:{example_count}, Length:{len(optimized_prompt)}"

    return scores


def score_with_judge(optimized_prompt: str, original_prompt: str, task: str) -> ScoreBreakdown:
    """Score using the Judge agent for more accurate evaluation."""
    try:
        llm_client = LLMClient()
        judge = LegacyJudge(llm_client)

        evaluation_request = f"""Evaluate this optimized prompt for quality.

Original prompt: "{original_prompt}"
Task: {task}

Optimized prompt:
---
{optimized_prompt}
---

Score the optimization on a 1-5 scale for each criterion."""

        judgment = judge.evaluate(
            request=evaluation_request,
            response=optimized_prompt,
            rubric="""
- Comprehensiveness: Does it include role, context, task, format, examples, and constraints?
- Structure: Are sections clearly organized with consistent delimiters (XML tags or markdown)?
- Examples: Are there 2+ diverse, realistic examples with input/output format?
- Actionability: Could someone use this prompt immediately without edits?
- Specificity: Are instructions precise rather than vague?
"""
        )

        # Convert 1-5 scores to 0-10
        scores = ScoreBreakdown()
        if judgment.scores:
            scores.comprehensiveness = judgment.scores.get("comprehensiveness", 3) * 2
            scores.structure_quality = judgment.scores.get("structure", 3) * 2
            scores.example_quality = judgment.scores.get("examples", 3) * 2
            scores.actionability = judgment.scores.get("actionability", 3) * 2
            scores.specificity = judgment.scores.get("specificity", 3) * 2

        scores.overall = judgment.overall_score * 2
        scores.reasoning = judgment.reasoning

        return scores

    except Exception as e:
        print(f"    Judge failed ({e}), using heuristics...")
        return score_with_heuristics(optimized_prompt)


async def test_variant(variant_name: str, system_prompt: str, test_case: dict) -> Optional[TestResult]:
    """Test a single variant on a single test case."""
    results = []

    async def capture_message(msg: dict):
        if msg.get("type") == "completed":
            results.append(msg.get("result", {}))

    try:
        # Create fresh agent
        agent = OptimizerAgent(model="gpt-4o-mini")

        # Monkey-patch the system prompt
        import agents.optimizer_agent as agent_module
        original_prompt = agent_module.AGENT_SYSTEM_PROMPT
        agent_module.AGENT_SYSTEM_PROMPT = system_prompt

        # Also update the agent's tool executor if needed
        agent = OptimizerAgent(model="gpt-4o-mini")

        try:
            state = await asyncio.wait_for(
                agent.run(
                    prompt_template=test_case["prompt"],
                    task_description=test_case["task"],
                    on_message=capture_message,
                ),
                timeout=120.0  # 2 minute timeout
            )

            if results and results[0].get("optimized_prompt"):
                optimized = results[0]["optimized_prompt"]

                # Score the output
                scores = score_with_heuristics(optimized)  # Use heuristics for speed

                return TestResult(
                    variant=variant_name,
                    test_name=test_case["name"],
                    prompt_length=len(optimized),
                    scores=scores,
                    optimized_prompt=optimized,
                )
        finally:
            # Always restore
            agent_module.AGENT_SYSTEM_PROMPT = original_prompt

    except asyncio.TimeoutError:
        print("TIMEOUT", end="")
    except Exception as e:
        print(f"ERROR({type(e).__name__})", end="")

    return None


async def run_ab_test():
    """Run A/B test across all variants and test cases."""
    print("=" * 70)
    print("A/B Testing System Prompts for Optimizer Agent")
    print("=" * 70)
    print(f"\nVariants: {list(PROMPT_VARIANTS.keys())}")
    print(f"Test cases: {[t['name'] for t in TEST_CASES]}")
    print()

    all_results: dict[str, list[TestResult]] = {name: [] for name in PROMPT_VARIANTS}

    for variant_name, system_prompt in PROMPT_VARIANTS.items():
        print(f"\n[{variant_name}]")
        print("-" * 50)

        for test_case in TEST_CASES:
            print(f"  {test_case['name']:20s} ... ", end="", flush=True)
            result = await test_variant(variant_name, system_prompt, test_case)

            if result:
                all_results[variant_name].append(result)
                print(f"Score: {result.scores.overall:5.1f} | Len: {result.prompt_length:5d} | {result.scores.reasoning[:40]}")
            else:
                print("FAILED")

    # Summary
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)

    # Build comparison table
    print(f"\n{'Variant':<20} | ", end="")
    for tc in TEST_CASES:
        print(f"{tc['name'][:12]:>12} | ", end="")
    print(f"{'Average':>8} |")
    print("-" * (24 + 15 * len(TEST_CASES) + 12))

    variant_averages = {}
    for variant_name, results in all_results.items():
        if results:
            print(f"{variant_name:<20} | ", end="")

            scores_by_test = {r.test_name: r.scores.overall for r in results}
            for tc in TEST_CASES:
                score = scores_by_test.get(tc["name"], 0)
                print(f"{score:>12.1f} | ", end="")

            avg_score = sum(r.scores.overall for r in results) / len(results)
            variant_averages[variant_name] = avg_score
            print(f"{avg_score:>8.1f} |")

    # Winner
    if variant_averages:
        winner = max(variant_averages, key=variant_averages.get)
        print(f"\n{'=' * 70}")
        print(f"WINNER: {winner}")
        print(f"Average Score: {variant_averages[winner]:.2f}/10")
        print("=" * 70)

        # Save winning variant
        if winner != "current":
            variant_path = f"scripts/prompt_variants/{winner}.txt"
            with open(variant_path, "w") as f:
                f.write(PROMPT_VARIANTS[winner])
            print(f"\nWinning prompt saved to: {variant_path}")

        # Show score breakdown for winner
        winner_results = all_results[winner]
        if winner_results:
            print(f"\n{winner} Score Breakdown:")
            for r in winner_results:
                print(f"  {r.test_name}:")
                print(f"    Comprehensiveness: {r.scores.comprehensiveness:.1f}")
                print(f"    Structure:         {r.scores.structure_quality:.1f}")
                print(f"    Examples:          {r.scores.example_quality:.1f}")
                print(f"    Actionability:     {r.scores.actionability:.1f}")
                print(f"    Specificity:       {r.scores.specificity:.1f}")


if __name__ == "__main__":
    asyncio.run(run_ab_test())
