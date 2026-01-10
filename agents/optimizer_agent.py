"""
Agent-based Prompt Optimizer

Uses an LLM agent loop with tools to optimize prompts. The agent decides:
- Whether to analyze the prompt
- Whether to search the web for few-shot examples
- Whether to ask the user clarification questions
- When to generate the final optimized prompt
"""

import json
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Literal
from datetime import datetime

from llm.client import chat_with_tools, create_tool_result_message, ChatWithToolsResponse
from agents.web_researcher import WebResearcher


# =============================================================================
# Tool Definitions (OpenAI format)
# =============================================================================

OPTIMIZER_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "analyze_prompt",
            "description": "Analyze the prompt to identify issues and score it against best practices. Call this first to understand what needs improvement.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt_text": {
                        "type": "string",
                        "description": "The prompt text to analyze"
                    }
                },
                "required": ["prompt_text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for few-shot examples and prompt patterns. Only use if the prompt would significantly benefit from real-world examples.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for finding relevant examples"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ask_user_question",
            "description": "Ask the user a clarifying question. Only use for critical ambiguities that significantly affect optimization. Max 3 questions per session.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question to ask the user"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Brief explanation of why this question helps optimization"
                    }
                },
                "required": ["question", "reason"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_optimized_prompt",
            "description": "Generate the final optimized prompt. Focus on CLARITY and STRUCTURE over length. Include: (1) Clear role, (2) XML sections as needed, (3) 2-3 quality examples, (4) Essential constraints. Remove fluff - every word must earn its place.",
            "parameters": {
                "type": "object",
                "properties": {
                    "optimized_prompt": {
                        "type": "string",
                        "description": "The optimized prompt text. Well-structured with XML tags, 2-3 examples, clear format spec. Concise but complete - no redundancy."
                    },
                    "improvements": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of specific improvements made"
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Brief explanation of why these changes improve the prompt"
                    },
                    "original_score": {
                        "type": "number",
                        "description": "Estimated score of the original prompt (0-10)"
                    },
                    "optimized_score": {
                        "type": "number",
                        "description": "Estimated score of the optimized prompt (0-10)"
                    }
                },
                "required": ["optimized_prompt", "improvements", "reasoning", "original_score", "optimized_score"]
            }
        }
    }
]


AGENT_SYSTEM_PROMPT = """You are an expert prompt optimization agent applying 2025 best practices from OpenAI, Anthropic, and Google DeepMind.

## Research-Backed Core Principles

1. **Conciseness wins**: LLMs degrade at ~3,000 tokens. Focused prompts outperform verbose ones.
2. **Structure beats length**: XML tags and formatting matter more than word count.
3. **Information density**: Every sentence must earn its place. No fluff.
4. **Quality > quantity**: 2-3 excellent examples beat 6 mediocre ones.

## Available Tools

1. **analyze_prompt**: Score 0-10, identify issues. ALWAYS call first.
2. **search_web**: Find examples for complex/domain-specific tasks.
3. **ask_user_question**: ONE question for CRITICAL ambiguities only (max 3/session).
4. **generate_optimized_prompt**: Output the final prompt.

## Optimization Techniques (Apply What's Needed)

### 1. Role Definition (Anthropic)
- Specific persona: "You are a [title] specializing in [domain]"
- Add behavioral traits only if they affect output quality

### 2. Structured Sections (Google)
- Use XML tags: <role>, <context>, <task>, <format>, <examples>, <constraints>
- Include only sections the task requires - don't force unnecessary structure
- Consistent delimiters throughout (don't mix XML and markdown headers)

### 3. Direct Instructions (OpenAI)
- Precise action verbs, explicit success criteria
- AVOID vague words: "good", "appropriate", "relevant", "proper", "suitable"
- Place critical instructions at the start, not buried in the middle

### 4. Output Format Specification (OpenAI)
- Explicit format: JSON schema, markdown structure, bullet template
- Length/verbosity guidance when relevant
- Show one structural example if format is complex

### 5. Few-Shot Examples (Google)
- 2-3 high-quality, diverse examples (typical + edge case)
- Format: <example><input>...</input><output>...</output></example>
- Add <thinking> tags only for complex reasoning tasks
- Examples should demonstrate exact expected format

### 6. Constraints & Boundaries (OpenAI)
- 3-5 essential "DO NOT" rules for likely failure modes
- Scope limits: what's in/out of bounds
- One escape hatch: "If uncertain about X, [action]"

### 7. Reasoning Guidance (Anthropic)
- For complex tasks: "Think step by step before answering"
- For multi-step: numbered process with clear handoffs
- Only add if task genuinely requires deliberate reasoning

## Target Lengths

- Simple tasks: 100-200 words
- Moderate tasks: 200-400 words
- Complex tasks: 400-600 words
- Beyond 600: likely too verbose - cut ruthlessly

## Process

1. Analyze: What's missing? What's excess?
2. Apply only the techniques the prompt actually needs
3. Test each element: "Does removing this hurt output?" If no, remove it.

## Quality Checklist

✓ Clear role with relevant expertise
✓ Structured with appropriate XML sections
✓ Direct, precise instructions (no vague words)
✓ Explicit output format
✓ 2-3 quality examples
✓ Essential constraints only
✓ Immediately usable without edits

**Principle: Maximum clarity, minimum words. Structure over length.**"""


# =============================================================================
# WebSocket Message Types
# =============================================================================

@dataclass
class WebSocketMessage:
    """Base class for WebSocket messages."""
    type: str
    data: dict = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps({"type": self.type, **self.data})


def msg_tool_called(tool_name: str, args: dict, result_summary: str = "") -> dict:
    """Create a tool_called message."""
    return {
        "type": "tool_called",
        "tool": tool_name,
        "args": args,
        "result_summary": result_summary[:200] if result_summary else "",
    }


def msg_question(question_id: str, question: str, reason: str) -> dict:
    """Create a question message for user input."""
    return {
        "type": "question",
        "question_id": question_id,
        "question": question,
        "reason": reason,
    }


def msg_progress(step: str, message: str) -> dict:
    """Create a progress update message."""
    return {
        "type": "progress",
        "step": step,
        "message": message,
    }


def msg_completed(result: dict) -> dict:
    """Create a completed message with final result."""
    return {
        "type": "completed",
        "result": result,
    }


def msg_error(error: str) -> dict:
    """Create an error message."""
    return {
        "type": "error",
        "error": error,
    }


# =============================================================================
# Agent State
# =============================================================================

@dataclass
class AgentState:
    """Mutable state for the optimizer agent."""
    messages: list[dict] = field(default_factory=list)
    tool_calls_made: list[dict] = field(default_factory=list)
    questions_asked: int = 0
    max_questions: int = 3
    web_sources: list[dict] = field(default_factory=list)
    analysis_result: Optional[dict] = None
    final_result: Optional[dict] = None
    error: Optional[str] = None
    status: Literal["running", "awaiting_input", "completed", "failed"] = "running"
    pending_question: Optional[dict] = None  # Current question awaiting answer


# =============================================================================
# Tool Implementations
# =============================================================================

class ToolExecutor:
    """Executes tools and returns results."""

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.web_researcher = WebResearcher(model=model)
        self.original_prompt = ""  # Store for use in generate_optimized

    async def execute(
        self,
        tool_name: str,
        args: dict,
        state: AgentState,
    ) -> tuple[str, Optional[dict]]:
        """
        Execute a tool and return the result.

        Returns:
            Tuple of (result_string, optional_special_action)
            special_action can be {"pause": question_data} or {"complete": result_data}
        """
        if tool_name == "analyze_prompt":
            return await self._analyze_prompt(args, state)
        elif tool_name == "search_web":
            return await self._search_web(args, state)
        elif tool_name == "ask_user_question":
            return self._ask_user_question(args, state)
        elif tool_name == "generate_optimized_prompt":
            return self._generate_optimized(args, state, self.original_prompt)
        else:
            return f"Unknown tool: {tool_name}", None

    async def _analyze_prompt(self, args: dict, state: AgentState) -> tuple[str, None]:
        """Analyze a prompt and return issues/score."""
        prompt_text = args.get("prompt_text", "")

        # Use the existing analyzer logic (simplified inline version)
        analysis_prompt = f"""Analyze this prompt against best practices:

---
{prompt_text}
---

Return a JSON object with:
{{
  "score": <0-10>,
  "issues": [
    {{"category": "clarity|structure|role|format|examples|constraints", "description": "...", "severity": "high|medium|low"}}
  ],
  "strengths": ["..."],
  "overall_quality": "good|fair|poor",
  "priority_improvements": ["list of top improvements"],
  "needs_examples": <true if few-shot examples would significantly help>,
  "ambiguities": ["list any critical ambiguities that need user clarification"]
}}"""

        from llm.client import chat
        result = chat(self.model, [
            {"role": "system", "content": "You are a prompt analysis expert. Return only valid JSON."},
            {"role": "user", "content": analysis_prompt}
        ])

        # Parse the JSON result for structured storage
        try:
            parsed = json.loads(result)
            state.analysis_result = parsed
        except json.JSONDecodeError:
            # If parsing fails, store as dict with raw content
            state.analysis_result = {"raw": result, "issues": [], "strengths": [], "overall_quality": "unknown", "priority_improvements": []}

        return result, None

    async def _search_web(self, args: dict, state: AgentState) -> tuple[str, None]:
        """Search the web for examples."""
        query = args.get("query", "")

        if not self.web_researcher.is_available:
            return "Web search is not available (TAVILY_API_KEY not configured). Proceed without examples.", None

        try:
            result = await self.web_researcher.search(query, max_results=3)
            sources = []
            for r in result.get("results", []):
                sources.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "snippet": r.get("content", "")[:500],
                })
            state.web_sources.extend(sources)

            return json.dumps({
                "sources": sources,
                "note": "Use these examples to inform your optimization if relevant."
            }), None

        except Exception as e:
            return f"Web search failed: {str(e)}. Proceed without examples.", None

    def _ask_user_question(self, args: dict, state: AgentState) -> tuple[str, dict]:
        """Ask user a clarifying question - pauses the agent."""
        question = args.get("question", "")
        reason = args.get("reason", "")

        if state.questions_asked >= state.max_questions:
            return f"Cannot ask more questions (max {state.max_questions} reached). Proceed with current information.", None

        state.questions_asked += 1
        state.status = "awaiting_input"
        state.pending_question = {
            "question": question,
            "reason": reason,
        }

        # Return special action to pause
        return "Waiting for user response...", {"pause": state.pending_question}

    def _generate_optimized(self, args: dict, state: AgentState, original_prompt: str = "") -> tuple[str, dict]:
        """Generate the final optimized prompt - completes the agent."""
        # Ensure analysis has the expected structure for the frontend
        analysis = state.analysis_result
        if analysis and isinstance(analysis, dict):
            # Ensure all expected fields exist
            if "issues" not in analysis:
                analysis["issues"] = []
            if "strengths" not in analysis:
                analysis["strengths"] = []
            if "overall_quality" not in analysis:
                analysis["overall_quality"] = "unknown"
            if "priority_improvements" not in analysis:
                analysis["priority_improvements"] = []

        result = {
            "original_prompt": original_prompt,  # Include original prompt
            "optimized_prompt": args.get("optimized_prompt", ""),
            "improvements": args.get("improvements", []),
            "reasoning": args.get("reasoning", ""),
            "original_score": args.get("original_score", 5.0),
            "optimized_score": args.get("optimized_score", 7.0),
            "web_sources": state.web_sources,
            "analysis": analysis,
            "few_shot_research": None,  # Agent mode doesn't use this
            "file_context": None,  # Agent mode doesn't use this
        }

        state.final_result = result
        state.status = "completed"

        return "Optimization complete.", {"complete": result}


# =============================================================================
# Optimizer Agent
# =============================================================================

class OptimizerAgent:
    """
    Agent-based prompt optimizer.

    Runs an LLM loop that decides which tools to use for optimization.
    Communicates progress via a callback function (for WebSocket updates).
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        max_iterations: int = 10,
    ):
        self.model = model
        self.max_iterations = max_iterations
        self.tool_executor = ToolExecutor(model=model)

    async def run(
        self,
        prompt_template: str,
        task_description: str,
        on_message: Callable[[dict], Any],
        initial_state: Optional[AgentState] = None,
        user_answer: Optional[str] = None,
        output_format: Optional[str] = None,
    ) -> AgentState:
        """
        Run the optimizer agent.

        Args:
            prompt_template: The prompt to optimize
            task_description: What the prompt should do
            on_message: Callback for WebSocket messages (async or sync)
            initial_state: Optional state to resume from
            user_answer: Optional answer to pending question (for resume)
            output_format: Desired output format (markdown, json, etc.)

        Returns:
            Final AgentState with result or pending question
        """
        # Store original prompt for use in result
        self.tool_executor.original_prompt = prompt_template

        # Initialize or resume state
        if initial_state:
            state = initial_state
            if user_answer and state.pending_question:
                # User answered a question - update the tool result with their answer
                answer_msg = f"User answered: {user_answer}"
                # Find the tool result for ask_user_question and update it
                # It should have content "Waiting for user response..."
                updated = False
                for i in range(len(state.messages) - 1, -1, -1):
                    msg = state.messages[i]
                    if msg.get("role") == "tool" and "Waiting for user response" in msg.get("content", ""):
                        state.messages[i]["content"] = answer_msg
                        updated = True
                        break
                if not updated:
                    # Fallback: find the last tool result and update it
                    for i in range(len(state.messages) - 1, -1, -1):
                        if state.messages[i].get("role") == "tool":
                            state.messages[i]["content"] = answer_msg
                            break
                state.pending_question = None
                state.status = "running"
        else:
            state = AgentState()
            # Build output format guidance if specified
            output_format_guidance = ""
            if output_format and output_format != "auto":
                format_descriptions = {
                    "markdown": "Markdown with proper headers, lists, code blocks, and formatting",
                    "json": "Valid JSON structure with clear schema",
                    "plain_text": "Simple unformatted plain text without special formatting",
                    "bullet_points": "Organized bullet point lists with clear hierarchy",
                    "step_by_step": "Numbered step-by-step instructions or procedures",
                    "table": "Tabular format using markdown tables or structured columns",
                    "code": "Programming code with proper syntax and comments",
                    "xml": "Well-formed XML with appropriate tags",
                    "conversation": "Dialogue or chat-style conversational format"
                }
                format_desc = format_descriptions.get(output_format, output_format)
                output_format_guidance = f"""

IMPORTANT - Required Output Format: {output_format.upper()}
The optimized prompt MUST explicitly instruct the model to respond in {format_desc}.
Include clear format specifications and ensure any examples demonstrate the {output_format} format."""

            # Build initial messages
            state.messages = [
                {"role": "system", "content": AGENT_SYSTEM_PROMPT},
                {"role": "user", "content": f"""Optimize this prompt:

Task Description: {task_description}

Prompt to Optimize:
---
{prompt_template}
---
{output_format_guidance}

Start by analyzing the prompt, then decide if you need web examples or user clarification, and finally generate the optimized version."""}
            ]

        await self._send(on_message, msg_progress("starting", "Beginning optimization..."))

        iteration = 0
        while iteration < self.max_iterations and state.status == "running":
            iteration += 1

            try:
                # Call LLM with tools
                response = chat_with_tools(
                    model=self.model,
                    messages=state.messages,
                    tools=OPTIMIZER_TOOLS,
                )

                # Add assistant message to history
                state.messages.append(response.to_message_dict())

                if response.has_tool_calls:
                    # Process each tool call
                    # First, collect all results before handling any special actions
                    # This ensures all tool_calls get responses even if one pauses
                    tool_results = []
                    pause_action = None
                    pause_tool_call_id = None
                    complete_action = None

                    for tool_call in response.tool_calls:
                        await self._send(on_message, msg_progress(
                            "tool",
                            f"Using {tool_call.name}..."
                        ))

                        # Execute the tool
                        result, action = await self.tool_executor.execute(
                            tool_call.name,
                            tool_call.arguments,
                            state,
                        )

                        # Log the tool call
                        state.tool_calls_made.append({
                            "tool": tool_call.name,
                            "args": tool_call.arguments,
                            "result_summary": result[:200] if result else "",
                        })

                        # Send tool update
                        await self._send(on_message, msg_tool_called(
                            tool_call.name,
                            tool_call.arguments,
                            result[:200] if result else ""
                        ))

                        # Store tool result
                        tool_results.append((tool_call.id, result))

                        # Check for special actions (but don't act yet)
                        if action:
                            if "pause" in action:
                                pause_action = action
                                pause_tool_call_id = tool_call.id
                            elif "complete" in action:
                                complete_action = action

                    # Add ALL tool results to conversation first
                    for tool_call_id, result in tool_results:
                        state.messages.append(create_tool_result_message(
                            tool_call_id,
                            result
                        ))

                    # Now handle special actions after all results are added
                    if pause_action:
                        question_data = pause_action["pause"]
                        await self._send(on_message, msg_question(
                            pause_tool_call_id,
                            question_data["question"],
                            question_data["reason"],
                        ))
                        return state  # Return to wait for answer

                    if complete_action:
                        await self._send(on_message, msg_completed(complete_action["complete"]))
                        return state

                elif response.finish_reason == "stop":
                    # Agent finished without calling generate_optimized
                    # Try to extract result from message content
                    if response.content:
                        state.final_result = {
                            "optimized_prompt": response.content,
                            "improvements": ["Agent provided direct response"],
                            "reasoning": "No structured output provided",
                            "original_score": 5.0,
                            "optimized_score": 6.0,
                            "web_sources": state.web_sources,
                        }
                        state.status = "completed"
                        await self._send(on_message, msg_completed(state.final_result))
                        return state

            except Exception as e:
                state.error = str(e)
                state.status = "failed"
                await self._send(on_message, msg_error(str(e)))
                return state

        # Max iterations reached
        if state.status == "running":
            state.status = "failed"
            state.error = "Max iterations reached without completion"
            await self._send(on_message, msg_error(state.error))

        return state

    async def _send(self, on_message: Callable, msg: dict):
        """Send a message via the callback."""
        import asyncio
        if asyncio.iscoroutinefunction(on_message):
            await on_message(msg)
        else:
            on_message(msg)
