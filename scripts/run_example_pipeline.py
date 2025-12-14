#!/usr/bin/env python3
"""
Example Pipeline Script

Demonstrates the full flow:
User Input -> Planner -> Worker Skill -> Judge -> Results

Usage:
    python run_example_pipeline.py          # Use mock LLM (default)
    python run_example_pipeline.py --real   # Use real OpenAI API
"""

import argparse
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents import Planner, Judge
from llm import MockLLMClient, OpenAIClient, LLMClient
from prompts import SkillRegistry


def create_llm_client(use_real: bool = False) -> LLMClient:
    """
    Create an LLM client.

    Args:
        use_real: If True, use OpenAI API. Otherwise use mock.

    Returns:
        An LLM client instance.
    """
    if use_real:
        print("[Using OpenAI API - gpt-4o-mini]")
        return OpenAIClient()
    else:
        print("[Using Mock LLM]")
        return MockLLMClient()


def run_pipeline(user_request: str, llm: LLMClient | None = None, verbose: bool = True) -> dict:
    """
    Run the full pipeline for a user request.

    Args:
        user_request: The user's input text.
        llm: LLM client to use. If None, creates a MockLLMClient with demo responses.
        verbose: Whether to print progress.

    Returns:
        Dict with plan, response, and judgment.
    """
    # Initialize components
    registry = SkillRegistry()

    # Use provided LLM or create mock with demo responses
    if llm is None:
        llm = MockLLMClient()
        # Configure mock responses for demo
        llm.queue_responses([
            # Planner response
            '''{
                "reasoning": "The user wants to debug code, so code_debugger is the best match.",
                "steps": [
                    {
                        "skill": "code_debugger",
                        "input_mapping": {"input": "user_request"},
                        "notes": "Analyze the code for issues"
                    }
                ]
            }''',
            # Worker skill response
            '''## Code Analysis

            I found the following issues:

            1. **Logic Error (Line 5)**: The loop condition `i <= len(arr)` should be `i < len(arr)` to avoid IndexError.

            2. **Performance Issue**: Consider using a set for O(1) lookups instead of the nested loop.

            ### Fixed Code:
            ```python
            def find_duplicates(arr):
                seen = set()
                duplicates = set()
                for item in arr:
                    if item in seen:
                        duplicates.add(item)
                    seen.add(item)
                return list(duplicates)
            ```
            ''',
            # Judge response
            '''{
                "scores": {
                    "accuracy": 5,
                    "completeness": 4,
                    "clarity": 5,
                    "helpfulness": 5
                },
                "overall_score": 5,
                "strengths": [
                    "Correctly identified the IndexError bug",
                    "Provided an optimized solution",
                    "Clear formatting with code examples"
                ],
                "weaknesses": [
                    "Could explain the time complexity improvement"
                ],
                "reasoning": "The response accurately identified the bugs, explained why they're problems, and provided a better solution with clean code."
            }''',
        ])

    planner = Planner(llm, registry)
    judge = Judge(llm)

    if verbose:
        print("=" * 60)
        print("PROMPT OPTIMIZATION PIPELINE DEMO")
        print("=" * 60)
        print(f"\nUser Request:\n{user_request}\n")

    # Step 1: Plan
    if verbose:
        print("-" * 40)
        print("Step 1: PLANNER")
        print("-" * 40)

    plan = planner.plan(user_request)

    if verbose:
        print(f"Reasoning: {plan.reasoning}")
        print(f"Selected skills: {plan.skill_names}")
        for i, step in enumerate(plan.steps, 1):
            print(f"  Step {i}: {step.skill}")
            if step.notes:
                print(f"          Notes: {step.notes}")

    # Validate plan
    is_valid, errors = planner.validate_plan(plan)
    if not is_valid:
        if verbose:
            print(f"\nPlan validation failed: {errors}")
        return {"error": "Plan validation failed", "errors": errors}

    # Step 2: Execute skill(s)
    if verbose:
        print("\n" + "-" * 40)
        print("Step 2: WORKER SKILL")
        print("-" * 40)

    responses = []
    for step in plan.steps:
        skill = registry.get(step.skill)
        if not skill:
            continue

        # Render the prompt
        prompt = skill.render(input=user_request)

        if verbose:
            print(f"\nExecuting skill: {skill.name}")
            print(f"Model: {skill.model}")
            print(f"Prompt preview: {prompt[:100]}...")

        # Call the LLM
        response = llm.complete(
            prompt,
            model=skill.model,
            max_tokens=skill.max_tokens,
            temperature=skill.temperature,
        )
        responses.append(response.content)

        if verbose:
            print(f"\nResponse:\n{response.content}")

    final_response = "\n\n".join(responses)

    # Step 3: Judge
    if verbose:
        print("\n" + "-" * 40)
        print("Step 3: JUDGE")
        print("-" * 40)

    judgment = judge.evaluate(user_request, final_response)

    if verbose:
        print(f"\nOverall Score: {judgment.overall_score}/5")
        print(f"Passed: {'Yes' if judgment.passed else 'No'}")
        print("\nScores by criterion:")
        for criterion, score in judgment.scores.items():
            print(f"  {criterion}: {score}/5")
        print(f"\nStrengths: {', '.join(judgment.strengths)}")
        print(f"Weaknesses: {', '.join(judgment.weaknesses)}")
        print(f"\nReasoning: {judgment.reasoning}")

    if verbose:
        print("\n" + "=" * 60)
        print("PIPELINE COMPLETE")
        print("=" * 60)

    return {
        "plan": plan,
        "response": final_response,
        "judgment": judgment,
    }


def demo_pairwise_comparison():
    """Demonstrate pairwise comparison between two responses."""
    llm = MockLLMClient()

    # Mock pairwise judgment response
    llm.queue_response('''{
        "winner": "B",
        "confidence": "high",
        "comparison": {
            "accuracy": {
                "winner": "tie",
                "explanation": "Both responses are factually correct"
            },
            "completeness": {
                "winner": "B",
                "explanation": "Response B includes additional context"
            },
            "clarity": {
                "winner": "B",
                "explanation": "Response B is better organized"
            }
        },
        "reasoning": "Response B is more complete and better organized while maintaining accuracy."
    }''')

    judge = Judge(llm)

    request = "What is Python?"
    response_a = "Python is a programming language."
    response_b = "Python is a high-level, interpreted programming language known for its readable syntax. It's widely used for web development, data science, and automation."

    print("=" * 60)
    print("PAIRWISE COMPARISON DEMO")
    print("=" * 60)
    print(f"\nRequest: {request}")
    print(f"\nResponse A: {response_a}")
    print(f"\nResponse B: {response_b}")

    result = judge.compare(request, response_a, response_b)

    print(f"\n{'='*40}")
    print(f"Winner: Response {result.winner}")
    print(f"Confidence: {result.confidence}")
    print(f"\nReasoning: {result.reasoning}")
    print("\nBy criterion:")
    for criterion, data in result.comparison.items():
        print(f"  {criterion}: {data.get('winner', 'tie')} - {data.get('explanation', '')}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run the prompt optimization pipeline demo"
    )
    parser.add_argument(
        "--real",
        action="store_true",
        help="Use real OpenAI API instead of mock (requires OPENAI_API_KEY env var)",
    )
    parser.add_argument(
        "--skip-pairwise",
        action="store_true",
        help="Skip the pairwise comparison demo",
    )
    args = parser.parse_args()

    # Example user request
    user_request = """
    Please help me debug this Python code:

    def find_duplicates(arr):
        duplicates = []
        for i in range(len(arr)):
            for j in range(i + 1, len(arr)):
                if arr[i] == arr[j] and arr[i] not in duplicates:
                    duplicates.append(arr[i])
        return duplicates

    It seems slow with large arrays.
    """

    # Create LLM client
    llm = create_llm_client(use_real=args.real) if args.real else None

    # Run main pipeline
    result = run_pipeline(user_request, llm=llm)

    if not args.skip_pairwise and not args.real:
        print("\n")
        # Run pairwise demo (only with mock to avoid extra API calls)
        demo_pairwise_comparison()
    elif args.real:
        print("\n[Skipping pairwise demo to minimize API calls]")


if __name__ == "__main__":
    main()
