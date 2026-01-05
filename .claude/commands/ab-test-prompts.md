---
description: Research, generate, and A/B test system prompts for the optimizer
---

You are an expert prompt engineer conducting research-driven A/B testing to find the optimal system prompt for the prompt optimizer agent.

## Phase 1: Research (REQUIRED FIRST)

Search the web for the latest prompt engineering best practices:

1. Search: "prompt engineering best practices 2025 system prompts"
2. Search: "OpenAI prompt engineering guide meta-prompts"
3. Search: "Anthropic Claude system prompt optimization"
4. Search: "few-shot prompting techniques research papers"

Synthesize findings into key principles for writing system prompts that generate high-quality outputs.

## Phase 2: Generate Variants

Based on your research, create 3-4 system prompt variants for `agents/optimizer_agent.py`. Each variant should:

- Have a clear hypothesis (e.g., "More structure = better output")
- Apply specific techniques from research
- Be meaningfully different from others

Variant ideas:
- **Structure-focused**: Strict XML template requirements
- **Example-focused**: Emphasize few-shot examples above all
- **Reasoning-focused**: Chain-of-thought, step-by-step analysis
- **Constraint-focused**: Heavy emphasis on DO NOT rules
- **Persona-focused**: Strong expert identity and behavioral guidelines

## Phase 3: Improved Scoring

Use the Judge agent to evaluate outputs. For each optimized prompt, score:

1. **Comprehensiveness** (0-10): Does it cover role, context, task, format, examples, constraints?
2. **Structure Quality** (0-10): Consistent delimiters, logical flow, clear sections?
3. **Example Quality** (0-10): Are examples diverse, realistic, well-formatted?
4. **Actionability** (0-10): Could someone use this prompt immediately with no edits?
5. **Specificity** (0-10): Are instructions precise or vague?

Call the Judge API or use manual evaluation rubric.

## Phase 4: Run Tests

Test prompts to optimize:
1. "Write a poem" (simple, creative)
2. "Summarize this article" (medium, analytical)
3. "Build a customer service bot" (complex, multi-step)
4. "Generate SQL from natural language" (technical, precise)

For each variant × test case:
1. Update `AGENT_SYSTEM_PROMPT` in `agents/optimizer_agent.py:117`
2. Run: `curl -X POST http://localhost:8000/api/v1/agents/optimize/start -H "Content-Type: application/json" -d '{"prompt_template": "...", "task_description": "..."}'`
3. Connect WebSocket and capture result
4. Score the output
5. Restore original prompt

## Phase 5: Report

```markdown
## Research Summary
[Key findings from web research]

## Variants Tested
### Variant A: [Name]
Hypothesis: [what you're testing]
Key changes: [bullet points]

### Variant B: [Name]
...

## Results

| Variant | Simple | Medium | Complex | Technical | Average |
|---------|--------|--------|---------|-----------|---------|
| A       | 8.2    | 7.5    | 9.0     | 8.1       | 8.2     |
| B       | ...    | ...    | ...     | ...       | ...     |

## Winner: [Variant Name]

### Why It Won
[Analysis of what made this variant effective]

### Recommended System Prompt
[The winning prompt, ready to copy into optimizer_agent.py]
```

## Important

- Always restore the original system prompt after testing
- Save all generated variants to `scripts/prompt_variants/` for future reference
- If a test fails, note it and continue with others
