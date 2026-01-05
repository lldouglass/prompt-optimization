"""WebSocket endpoint for agent-based prompt optimization."""

import json
import asyncio
from uuid import UUID
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import AgentSession

# Import the agent - use try/except for graceful handling if not available
try:
    from agents.optimizer_agent import OptimizerAgent, AgentState
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False
    OptimizerAgent = None
    AgentState = None

router = APIRouter(prefix="/ws", tags=["websocket"])


async def get_session_by_id(
    session_id: str,
    org_id: UUID,
    db: AsyncSession,
) -> Optional[AgentSession]:
    """Get an agent session by ID, validating org ownership."""
    try:
        uuid_id = UUID(session_id)
    except ValueError:
        return None

    result = await db.execute(
        select(AgentSession).where(
            AgentSession.id == uuid_id,
            AgentSession.org_id == org_id,
        )
    )
    return result.scalar_one_or_none()


@router.websocket("/optimize/{session_id}")
async def optimize_websocket(
    websocket: WebSocket,
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    WebSocket endpoint for agent-based optimization.

    Flow:
    1. Client starts optimization via POST /api/v1/agents/optimize/start
    2. Client connects to this WebSocket with the session_id
    3. Agent runs and sends progress updates
    4. If agent asks a question, client receives it and sends answer back
    5. Agent continues until completion or error

    Message types sent to client:
    - {"type": "progress", "step": "...", "message": "..."}
    - {"type": "tool_called", "tool": "...", "args": {...}, "result_summary": "..."}
    - {"type": "question", "question_id": "...", "question": "...", "reason": "..."}
    - {"type": "completed", "result": {...}}
    - {"type": "error", "error": "..."}

    Message types received from client:
    - {"type": "answer", "question_id": "...", "answer": "..."}
    """
    await websocket.accept()

    # Validate session exists
    # Note: In production, you'd validate the session's org matches the authenticated user
    # For now, we'll get org from cookie if available
    try:
        # Try to get session
        result = await db.execute(
            select(AgentSession).where(AgentSession.id == UUID(session_id))
        )
        session = result.scalar_one_or_none()

        if not session:
            await websocket.send_json({"type": "error", "error": "Session not found"})
            await websocket.close()
            return

        if session.is_expired():
            await websocket.send_json({"type": "error", "error": "Session expired"})
            await websocket.close()
            return

        if not AGENT_AVAILABLE:
            await websocket.send_json({"type": "error", "error": "Agent not available"})
            await websocket.close()
            return

        # Get initial request data
        initial_request = session.initial_request or {}
        prompt_template = initial_request.get("prompt_template", "")
        task_description = initial_request.get("task_description", "")
        output_format = initial_request.get("output_format")

        if not prompt_template:
            await websocket.send_json({"type": "error", "error": "No prompt template in session"})
            await websocket.close()
            return

        # Create message sender that enriches completed messages
        async def send_message(msg: dict):
            try:
                # Enrich completed message with missing fields the frontend expects
                if msg.get("type") == "completed" and msg.get("result"):
                    result = msg["result"]
                    # Add original_prompt if missing
                    if "original_prompt" not in result:
                        result["original_prompt"] = prompt_template
                    # Normalize field names - convert web_sources to few_shot_research format
                    if "few_shot_research" not in result:
                        result["few_shot_research"] = None
                    # Add file_context if missing
                    if "file_context" not in result:
                        result["file_context"] = None
                    # Ensure analysis has expected structure
                    if "analysis" in result and result["analysis"]:
                        analysis = result["analysis"]
                        if isinstance(analysis, dict):
                            analysis.setdefault("issues", [])
                            analysis.setdefault("strengths", [])
                            analysis.setdefault("overall_quality", "unknown")
                            analysis.setdefault("priority_improvements", [])
                await websocket.send_json(msg)
            except Exception as e:
                # Log the error but don't crash - connection may be closed
                import logging
                logging.warning(f"Failed to send WebSocket message: {e}")

        # Initialize agent
        agent = OptimizerAgent(model="gpt-4o-mini")

        # Restore state if resuming
        initial_state = None
        if session.conversation_history:
            initial_state = AgentState(
                messages=session.conversation_history,
                tool_calls_made=session.tool_calls_made or [],
                questions_asked=session.questions_asked_count or 0,
                web_sources=session.web_sources or [],
                analysis_result=session.current_analysis,
            )

        # Run agent
        user_answer = None
        while True:
            # Update session status
            session.status = "running"
            session.updated_at = datetime.utcnow()
            await db.commit()

            # Run agent iteration
            state = await agent.run(
                prompt_template=prompt_template,
                task_description=task_description,
                on_message=send_message,
                initial_state=initial_state,
                user_answer=user_answer,
                output_format=output_format,
            )

            # Save state to session
            session.conversation_history = state.messages
            session.tool_calls_made = state.tool_calls_made
            session.questions_asked_count = state.questions_asked
            session.web_sources = state.web_sources
            session.current_analysis = state.analysis_result
            session.status = state.status
            session.updated_at = datetime.utcnow()

            if state.status == "completed":
                session.result = state.final_result
                await db.commit()
                break

            elif state.status == "failed":
                session.error_message = state.error
                await db.commit()
                break

            elif state.status == "awaiting_input":
                session.pending_questions = [state.pending_question] if state.pending_question else []
                await db.commit()

                # Wait for user answer
                try:
                    data = await asyncio.wait_for(
                        websocket.receive_json(),
                        timeout=300.0  # 5 minute timeout for answer
                    )

                    if data.get("type") == "answer":
                        user_answer = data.get("answer", "")
                        initial_state = state
                        # Continue loop with answer
                    else:
                        await send_message({"type": "error", "error": "Expected answer message"})
                        break

                except asyncio.TimeoutError:
                    session.status = "failed"
                    session.error_message = "Timeout waiting for user answer"
                    await db.commit()
                    await send_message({"type": "error", "error": "Timeout waiting for answer"})
                    break

            else:
                # Unexpected status
                break

    except WebSocketDisconnect:
        # Client disconnected - update session
        if session:
            session.status = "failed"
            session.error_message = "Client disconnected"
            session.updated_at = datetime.utcnow()
            await db.commit()

    except Exception as e:
        try:
            await websocket.send_json({"type": "error", "error": str(e)})
        except Exception:
            pass
        if session:
            session.status = "failed"
            session.error_message = str(e)
            await db.commit()

    finally:
        try:
            await websocket.close()
        except Exception:
            pass
