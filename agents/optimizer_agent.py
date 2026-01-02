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
            "description": "Generate the final optimized version of the prompt. Call this when you have enough information to create an improved version.",
            "parameters": {
                "type": "object",
                "properties": {
                    "optimized_prompt": {
                        "type": "string",
                        "description": "The full optimized prompt text"
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


AGENT_SYSTEM_PROMPT = """You are a prompt optimization agent. Your job is to analyze prompts and improve them based on 2025 best practices from OpenAI, Anthropic, and Google DeepMind.

## Available Tools

1. **analyze_prompt**: Score the prompt (0-10) and identify issues. ALWAYS call this first.

2. **search_web**: Search for real-world few-shot examples. Only use if:
   - The prompt involves complex formatting or domain-specific output
   - Examples would significantly improve the prompt
   - The task is non-trivial and would benefit from demonstration

3. **ask_user_question**: Ask ONE clarifying question. Only use for CRITICAL ambiguities:
   - The target audience is unclear and affects tone/complexity
   - The output format could be multiple valid options
   - Key constraints are missing that would change the approach
   - DO NOT ask about obvious things or minor details
   - You have a maximum of 3 questions per session

4. **generate_optimized_prompt**: Output the final optimized prompt. Call when ready.

## Optimization Guidelines

Apply these best practices:
- **Clear Role**: Start with specific expertise ("You are a senior [role] specializing in [domain]")
- **Structured Sections**: Use XML tags (<context>, <task>, <format>) OR consistent markdown
- **Direct Instructions**: Be precise, avoid vague words like "good" or "appropriate"
- **Output Format**: Explicitly specify format, length, and verbosity
- **Constraints**: Include "DO NOT" instructions and escape hatches
- **Few-Shot Examples**: Include 2-4 examples when beneficial (from search or generated)

## Process

1. ALWAYS call analyze_prompt first
2. Decide if web search or user questions are needed (usually not - only for complex cases)
3. Generate the optimized prompt with all improvements

Be efficient - most prompts can be optimized with just analyze + generate. Only use search_web or ask_user_question when truly necessary."""


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
            return self._generate_optimized(args, state)
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
  "needs_examples": <true if few-shot examples would significantly help>,
  "ambiguities": ["list any critical ambiguities that need user clarification"]
}}"""

        from llm.client import chat
        result = chat(self.model, [
            {"role": "system", "content": "You are a prompt analysis expert. Return only valid JSON."},
            {"role": "user", "content": analysis_prompt}
        ])

        state.analysis_result = result
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

    def _generate_optimized(self, args: dict, state: AgentState) -> tuple[str, dict]:
        """Generate the final optimized prompt - completes the agent."""
        result = {
            "optimized_prompt": args.get("optimized_prompt", ""),
            "improvements": args.get("improvements", []),
            "reasoning": args.get("reasoning", ""),
            "original_score": args.get("original_score", 5.0),
            "optimized_score": args.get("optimized_score", 7.0),
            "web_sources": state.web_sources,
            "analysis": state.analysis_result,
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
    ) -> AgentState:
        """
        Run the optimizer agent.

        Args:
            prompt_template: The prompt to optimize
            task_description: What the prompt should do
            on_message: Callback for WebSocket messages (async or sync)
            initial_state: Optional state to resume from
            user_answer: Optional answer to pending question (for resume)

        Returns:
            Final AgentState with result or pending question
        """
        # Initialize or resume state
        if initial_state:
            state = initial_state
            if user_answer and state.pending_question:
                # Add the user's answer to conversation
                answer_msg = f"User answered: {user_answer}"
                # Find the tool call ID for the pending question
                # and add the answer as a tool result
                if state.messages and state.messages[-1].get("tool_calls"):
                    tool_call_id = state.messages[-1]["tool_calls"][-1]["id"]
                    state.messages.append(create_tool_result_message(tool_call_id, answer_msg))
                state.pending_question = None
                state.status = "running"
        else:
            state = AgentState()
            # Build initial messages
            state.messages = [
                {"role": "system", "content": AGENT_SYSTEM_PROMPT},
                {"role": "user", "content": f"""Optimize this prompt:

Task Description: {task_description}

Prompt to Optimize:
---
{prompt_template}
---

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

                        # Handle special actions
                        if action:
                            if "pause" in action:
                                # Agent is asking a question
                                question_data = action["pause"]
                                await self._send(on_message, msg_question(
                                    tool_call.id,
                                    question_data["question"],
                                    question_data["reason"],
                                ))
                                return state  # Return to wait for answer

                            elif "complete" in action:
                                # Agent finished
                                await self._send(on_message, msg_completed(action["complete"]))
                                return state

                        # Add tool result to conversation
                        state.messages.append(create_tool_result_message(
                            tool_call.id,
                            result
                        ))

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
