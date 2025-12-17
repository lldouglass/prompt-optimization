---
description: Automatically optimize prompts and apply best practices when users are writing or discussing LLM prompts
triggers:
  - writing prompts for LLMs
  - asking about prompt engineering
  - creating system prompts
  - optimizing AI instructions
---

# Prompt Optimization Skill

Use this skill when users are writing, discussing, or asking about prompts for LLMs.

## When to Activate

- User is writing a system prompt or instructions for an AI
- User asks "how should I prompt..." or "what's the best way to ask..."
- User shares a prompt and asks for feedback
- User is creating YAML skill files or prompt templates
- User mentions prompt engineering or prompt optimization

## Best Practices to Apply

### Structure (CO-STAR)
- **Context**: Provide relevant background
- **Objective**: State the task clearly
- **Style**: Define the writing approach
- **Tone**: Set the emotional quality
- **Audience**: Specify who will read output
- **Response**: Define format requirements

### Principles

1. **Role First**: Start with "You are a [specific expert]..."
2. **Explicit Instructions**: Say what TO do AND what NOT to do
3. **Output Format**: Specify JSON, markdown, length, etc.
4. **Chain of Thought**: Add "Think step by step" for complex reasoning
5. **Examples**: Include 1-3 examples for complex tasks
6. **Constraints**: Define scope and limitations
7. **Edge Cases**: Address ambiguous scenarios

### Anti-Patterns to Avoid
- Vague instructions ("do your best")
- Missing output format
- No role definition
- Unclear success criteria
- Overly long prompts without structure

## Evaluation Criteria

Rate prompts on:
- **Clarity** (1-5): Is the task unambiguous?
- **Structure** (1-5): Well-organized sections?
- **Specificity** (1-5): Explicit requirements?
- **Format** (1-5): Clear output expectations?

## Response Format

When optimizing, provide:
1. Brief analysis of current prompt
2. Specific issues identified
3. The optimized version
4. Explanation of changes
