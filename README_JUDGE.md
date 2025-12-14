# Judge Agent

The Judge agent evaluates LLM outputs using a structured rubric. It supports both single-output evaluation and pairwise comparison.

## Features

- **Single Evaluation**: Score an LLM output on correctness (0-4), completeness (0-3), clarity_and_style (0-2), and safety (0-1) for a total score of 0-10
- **Pairwise Comparison**: Compare two outputs and determine a winner with confidence margin (slightly/moderately/strongly)
- **Tagging**: Automatically tags outputs with labels like "hallucination", "missing_key_detail", "good", etc.
- **Error Handling**: Custom `JudgeError` exception for parsing failures

## Setup

The Judge requires an OpenAI API key. Set it via environment variable:

```bash
export OPENAI_API_KEY="your-key-here"
```

Or add it to a `.env` file in the project root.

## Usage

### Single Evaluation

```python
from agents.judge import Judge

judge = Judge(model="gpt-4o-mini")

result = judge.evaluate_single(
    task_description="Answer a factual question",
    user_input="What is Python?",
    candidate_output="Python is a high-level programming language.",
)

print(result["overall_score"])  # 0-10
print(result["subscores"])      # {"correctness": 4, "completeness": 3, ...}
print(result["tags"])           # ["good"]
print(result["rationale"])      # "Well-written response..."
```

### Pairwise Comparison

```python
result = judge.evaluate_pairwise(
    task_description="Explain a concept",
    user_input="What is recursion?",
    output_a="A function calling itself.",
    output_b="Recursion is when a function calls itself to solve subproblems.",
)

print(result["winner"])    # "A" or "B"
print(result["margin"])    # "slightly", "moderately", or "strongly"
print(result["rationale"]) # "B provides more detail..."
```

## Running the Demo

```bash
python scripts/demo_judge.py
```

## Running Tests

```bash
python -m pytest tests/test_judge.py -v
```

## API Reference

### `Judge(model: str = "gpt-4o-mini")`

Initialize the judge with the specified model.

### `evaluate_single(task_description, user_input, candidate_output, reference_answer=None) -> dict`

Returns: `{"overall_score", "subscores", "tags", "rationale"}`

### `evaluate_pairwise(task_description, user_input, output_a, output_b) -> dict`

Returns: `{"winner", "margin", "tags", "rationale"}`

### `JudgeError`

Raised when JSON parsing fails or required keys are missing.
