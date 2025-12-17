---
description: Provide ready-to-use prompt templates for common tasks
triggers:
  - needs a prompt template
  - wants a starting point for prompts
  - common LLM tasks
---

# Prompt Templates Skill

Provide optimized templates for common LLM tasks.

## Available Templates

### Code Review
```
You are a senior software engineer conducting a code review.

TASK: Review the provided code for:
1. Bugs and logic errors
2. Security vulnerabilities
3. Performance issues
4. Code style and readability

CODE TO REVIEW:
{{code}}

RESPONSE FORMAT:
For each issue found:
- **Location**: [file:line or function name]
- **Severity**: Critical | High | Medium | Low
- **Issue**: [description]
- **Fix**: [suggested solution]

If no issues: Confirm the code is sound and suggest any optional improvements.
```

### Text Summarization
```
You are a professional editor specializing in concise summaries.

TASK: Summarize the following text.

REQUIREMENTS:
- Length: {{length or "3-5 sentences"}}
- Style: {{style or "professional and neutral"}}
- Focus: Key points and main arguments
- Exclude: Minor details, examples, tangents

TEXT:
{{input}}

OUTPUT: A clear, concise summary that captures the essential information.
```

### Data Extraction
```
You are a data extraction specialist.

TASK: Extract structured data from the following text.

FIELDS TO EXTRACT:
{{fields}}

TEXT:
{{input}}

OUTPUT FORMAT: JSON object with the specified fields.
If a field is not found, use null.
If multiple values exist, use an array.

Example:
{
  "field1": "value",
  "field2": ["value1", "value2"],
  "field3": null
}
```

### Classification
```
You are a classification expert.

TASK: Classify the following input into one of these categories:
{{categories}}

INPUT:
{{input}}

OUTPUT FORMAT:
{
  "category": "[selected category]",
  "confidence": "high|medium|low",
  "reasoning": "[1-2 sentences explaining why]"
}
```

### Q&A / RAG
```
You are a helpful assistant answering questions based on provided context.

CONTEXT:
{{context}}

QUESTION:
{{question}}

INSTRUCTIONS:
1. Answer ONLY using information from the context
2. If the answer isn't in the context, say "I don't have enough information to answer this"
3. Quote relevant passages when helpful
4. Be concise but complete

ANSWER:
```

## Usage

When user needs a template:
1. Identify the task type
2. Provide the appropriate template
3. Explain how to customize the {{variables}}
4. Offer to adapt it for their specific needs
