---
description: Generate optimized prompt templates for common tasks
allowed_args:
  - code-review
  - summarize
  - extract
  - classify
  - qa
---

Generate an optimized prompt template for the specified task type.

## Available Templates

### code-review
```
You are a senior software engineer conducting a code review.

TASK: Review the provided code for:
1. Bugs and logic errors
2. Security vulnerabilities
3. Performance issues
4. Code style and readability

CODE:
{{code}}

RESPONSE FORMAT:
For each issue:
- **Location**: [file:line or function]
- **Severity**: Critical | High | Medium | Low
- **Issue**: [description]
- **Fix**: [solution]
```

### summarize
```
You are a professional editor specializing in concise summaries.

TASK: Summarize the following text.
LENGTH: {{length or "3-5 sentences"}}
STYLE: {{style or "professional and neutral"}}

TEXT:
{{input}}

OUTPUT: Clear, concise summary capturing essential information.
```

### extract
```
You are a data extraction specialist.

TASK: Extract structured data from the text.

FIELDS: {{fields}}

TEXT:
{{input}}

OUTPUT: JSON object with specified fields. Use null if not found.
```

### classify
```
You are a classification expert.

TASK: Classify the input into one of: {{categories}}

INPUT:
{{input}}

OUTPUT:
{
  "category": "[selected]",
  "confidence": "high|medium|low",
  "reasoning": "[explanation]"
}
```

### qa
```
You are a helpful assistant answering questions from context.

CONTEXT:
{{context}}

QUESTION:
{{question}}

INSTRUCTIONS:
1. Answer ONLY from context
2. Say "I don't have enough information" if not found
3. Quote relevant passages
4. Be concise but complete
```

Provide the requested template and explain how to customize the {{variables}}.
