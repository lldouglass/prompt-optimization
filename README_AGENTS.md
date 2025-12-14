# Agent Framework Documentation

A minimal, clean framework for LLM prompt orchestration with skill-based routing and output evaluation.

## Overview

This framework provides:

1. **Skill Registry** - YAML-based prompt templates with metadata
2. **Planner Agent** - Routes user requests to appropriate skills
3. **Judge Agent** - Evaluates outputs with rubrics and comparisons
4. **LLM Abstraction** - Pluggable interface for different providers

## Quick Start

```python
from agents import Planner, Judge
from llm import MockLLMClient  # Replace with your LLM client
from prompts import SkillRegistry

# Initialize
registry = SkillRegistry()
llm = MockLLMClient()
planner = Planner(llm, registry)
judge = Judge(llm)

# Create execution plan
plan = planner.plan("Summarize this document for me")
print(f"Selected skills: {plan.skill_names}")

# Execute skill
skill = registry.get(plan.steps[0].skill)
prompt = skill.render(input="Your document text here...")
response = llm.complete(prompt, model=skill.model)

# Evaluate output
judgment = judge.evaluate("Summarize this document", response.content)
print(f"Score: {judgment.overall_score}/5")
```

Run the example pipeline:

```bash
cd prompt-optimization
python scripts/run_example_pipeline.py
```

## Directory Structure

```
prompt-optimization/
├── prompts/
│   ├── __init__.py
│   ├── registry.py          # Skill loading and management
│   └── skills/
│       ├── summarize_long_doc.yaml
│       ├── code_debugger.yaml
│       └── general_assistant.yaml
├── agents/
│   ├── __init__.py
│   ├── planner.py            # Request routing
│   └── judge.py              # Output evaluation
├── llm/
│   ├── __init__.py
│   └── client.py             # LLM abstraction layer
├── scripts/
│   └── run_example_pipeline.py
└── tests/
    ├── test_planner.py
    └── test_judge.py
```

## Components

### Skill Registry

Skills are YAML files that define prompt templates with metadata:

```yaml
name: summarize_long_doc
description: Summarizes long documents into a structured outline
tags:
  - summarization
  - analysis
model: gpt-4.1
max_tokens: 1024
temperature: 0.3
prompt_template: |
  You are a summarization assistant.
  Summarize the document into key points.

  USER DOCUMENT:
  {{input}}
```

**Template Variables:**
- `{{variable}}` - Simple substitution
- `{{#if variable}}content{{/if}}` - Conditional blocks

**Usage:**

```python
from prompts import SkillRegistry

registry = SkillRegistry()

# Get a skill
skill = registry.get("code_debugger")

# Render prompt
prompt = skill.render(input="def foo():", language="python")

# Find by tag
code_skills = registry.get_by_tag("code")

# Get formatted catalog
catalog = registry.get_catalog()
```

### Planner Agent

Routes user requests to appropriate skills:

```python
from agents import Planner

planner = Planner(llm_client, registry)

# Create a plan
plan = planner.plan("Help me debug this code")

# Plan contains:
# - reasoning: Why these skills were chosen
# - steps: List of PlanStep objects
#   - skill: Skill name to execute
#   - input_mapping: How to map inputs
#   - notes: Additional instructions

# Validate the plan
is_valid, errors = planner.validate_plan(plan)
```

### Judge Agent

Evaluates outputs against rubrics:

```python
from agents import Judge

judge = Judge(llm_client)

# Single evaluation
judgment = judge.evaluate(
    request="What is Python?",
    response="Python is a programming language."
)
# judgment.overall_score: 1-5
# judgment.passed: True if score >= 3
# judgment.strengths: List of positives
# judgment.weaknesses: List of issues

# Pairwise comparison
result = judge.compare(
    request="What is Python?",
    response_a="It's a snake.",
    response_b="Python is a high-level programming language."
)
# result.winner: "A", "B", or "tie"
# result.confidence: "high", "medium", "low"
# result.comparison: Per-criterion breakdown
```

**Custom Rubrics:**

```python
custom_rubric = """
- Technical Accuracy: Is the code correct?
- Performance: Is the solution efficient?
- Security: Are there vulnerabilities?
"""

judge = Judge(llm_client, rubric=custom_rubric)
```

### LLM Client

Abstract interface for LLM providers:

```python
from llm import LLMClient, LLMResponse

class MyLLMClient(LLMClient):
    def complete(self, prompt, *, model, max_tokens, temperature, **kwargs):
        # Your implementation
        return LLMResponse(
            content="...",
            model=model,
            usage={"total_tokens": 100}
        )

    def complete_chat(self, messages, *, model, max_tokens, temperature, **kwargs):
        # Your implementation
        return LLMResponse(...)
```

**MockLLMClient** for testing:

```python
from llm import MockLLMClient

mock = MockLLMClient(default_response="Default")

# Queue specific responses
mock.queue_response("First response")
mock.queue_responses(["Second", "Third"])

# Check call history
print(mock.call_history)

# Reset state
mock.reset()
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_planner.py -v

# Run with coverage
pytest tests/ --cov=agents --cov=prompts --cov=llm
```

## Extending the Framework

### Adding New Skills

Create a new YAML file in `prompts/skills/`:

```yaml
name: my_new_skill
description: What this skill does
tags:
  - tag1
  - tag2
model: gpt-4.1
max_tokens: 2048
temperature: 0.5
prompt_template: |
  Your prompt template here.

  User input: {{input}}
```

### Implementing Real LLM Clients

Example OpenAI implementation:

```python
import openai
from llm import LLMClient, LLMResponse

class OpenAIClient(LLMClient):
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)

    def complete(self, prompt, *, model, max_tokens, temperature, **kwargs):
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return LLMResponse(
            content=response.choices[0].message.content,
            model=model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            raw_response=response,
        )

    def complete_chat(self, messages, *, model, max_tokens, temperature, **kwargs):
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return LLMResponse(
            content=response.choices[0].message.content,
            model=model,
            usage=dict(response.usage),
            raw_response=response,
        )
```

## Architecture Notes

- **No heavy frameworks** - Uses only Python stdlib + pydantic-style dataclasses
- **Pluggable LLM layer** - Easy to swap providers
- **YAML skills** - Non-developers can edit prompts
- **Robust parsing** - Fallback handling for malformed LLM responses
- **Test-friendly** - MockLLMClient enables deterministic testing
