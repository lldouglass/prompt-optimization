#!/usr/bin/env python3
"""
Demo script for the Judge agent.

Shows how to use evaluate_single and evaluate_pairwise methods.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.judge import Judge, JudgeError


def main():
    print("=" * 60)
    print("Judge Agent Demo")
    print("=" * 60)

    judge = Judge(model="gpt-4o-mini")

    # Example 1: Single evaluation
    print("\n--- Example 1: Single Evaluation ---\n")

    task_description = "Answer a factual question about Python"
    user_input = "What is a Python decorator?"
    candidate_output = """A decorator in Python is a function that takes another function 
as an argument and extends its behavior without explicitly modifying it. 
Decorators use the @symbol syntax and are commonly used for logging, 
authentication, and memoization."""

    try:
        result = judge.evaluate_single(
            task_description=task_description,
            user_input=user_input,
            candidate_output=candidate_output,
        )
        print(f"Overall Score: {result['overall_score']}/10")
        print(f"Subscores: {result['subscores']}")
        print(f"Tags: {result['tags']}")
        print(f"Rationale: {result['rationale']}")

    except NotImplementedError as e:
        print(f"LLM client not wired up yet; implement llm.client.chat() to run this demo.")
        print(f"Details: {e}")
        return

    except JudgeError as e:
        print(f"Judge error: {e}")
        return

    # Example 2: Pairwise comparison
    print("\n--- Example 2: Pairwise Comparison ---\n")

    task_description = "Explain recursion in programming"
    user_input = "What is recursion?"

    output_a = "Recursion is when a function calls itself."

    output_b = """Recursion is a programming technique where a function calls itself 
to solve a problem by breaking it down into smaller subproblems. Each recursive 
call works on a smaller piece of the original problem until reaching a base case 
that can be solved directly. Common examples include calculating factorials and 
traversing tree structures."""

    try:
        result = judge.evaluate_pairwise(
            task_description=task_description,
            user_input=user_input,
            output_a=output_a,
            output_b=output_b,
        )
        print(f"Winner: {result['winner']}")
        print(f"Margin: {result['margin']}")
        print(f"Tags: {result['tags']}")
        print(f"Rationale: {result['rationale']}")

    except NotImplementedError as e:
        print(f"LLM client not wired up yet; implement llm.client.chat() to run this demo.")
        print(f"Details: {e}")

    except JudgeError as e:
        print(f"Judge error: {e}")

    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
