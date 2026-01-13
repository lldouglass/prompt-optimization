"""LLM-based generation functions for video workflow steps."""

import asyncio
import json
import logging
import os
import uuid

import openai

logger = logging.getLogger(__name__)

from .mocks import (
    MOCK_MODE,
    get_mock_clarifying_questions,
    get_mock_continuity_pack,
    get_mock_shot_plan,
    get_mock_prompt_pack,
)
from .compiler import compile_all_shots


def _get_openai_client() -> openai.OpenAI:
    """Get OpenAI client with API key from environment."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not configured")
    return openai.OpenAI(api_key=api_key)


def _chat(messages: list[dict], model: str = "gpt-4o-mini") -> str:
    """Simple chat function using OpenAI directly."""
    client = _get_openai_client()
    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    return response.choices[0].message.content or ""


def _parse_json_response(content: str, default: str = "{}") -> dict | list:
    """Parse JSON from LLM response, handling markdown code blocks."""
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    elif "```" in content:
        content = content.split("```")[1].split("```")[0]
    return json.loads(content) if content.strip() else json.loads(default)


async def generate_clarifying_questions(brief: dict) -> list[dict]:
    """
    Generate 3-7 clarifying questions based on the brief.

    Args:
        brief: Brief intake data

    Returns:
        List of question dicts with id, question, category
    """
    logger.info(f"generate_clarifying_questions called with MOCK_MODE={MOCK_MODE}")
    logger.info(f"Brief for questions: {json.dumps(brief, indent=2)[:500]}")

    if MOCK_MODE:
        logger.info("Returning mock questions due to MOCK_MODE=True")
        return get_mock_clarifying_questions()

    # Build prompt for LLM
    system_prompt = """You are a professional video production planner. Based on a client brief, generate 3-7 clarifying questions to gather missing information needed for a complete video shot plan.

Question categories:
- shot_style: Questions about camera style (handheld, locked-off, dolly, drone)
- pacing: Questions about video rhythm and editing pace
- camera_movement: Questions about specific camera moves
- action_beats: Questions about specific actions to capture
- audio: Questions about sound design and dialogue
- cta: Questions about call-to-action requirements

Return a JSON array of objects with: id (uuid), question (string), category (string from above list).

Only ask questions about information NOT already provided in the brief. Be specific and actionable."""

    user_prompt = f"""Client Brief:
Project: {brief.get('project_name', 'Untitled')}
Goal: {brief.get('goal', 'Not specified')}
Platform: {brief.get('platform', 'Not specified')}
Duration: {brief.get('duration_seconds', 'Not specified')} seconds
Brand Vibe: {', '.join(brief.get('brand_vibe', []))}
Avoid: {', '.join(brief.get('avoid_vibe', []))}
Must Include: {', '.join(brief.get('must_include', []))}
Must Avoid: {', '.join(brief.get('must_avoid', []))}
Subject Description: {brief.get('product_or_subject_description', 'Not provided')}
Script/VO: {brief.get('script_or_vo', 'None')}

Generate clarifying questions for missing details needed for video production."""

    try:
        content = await asyncio.to_thread(
            _chat,
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        # Parse JSON response
        questions = _parse_json_response(content, "[]")

        # Ensure each question has an id
        for q in questions:
            if "id" not in q:
                q["id"] = str(uuid.uuid4())

        return questions[:7]  # Max 7 questions

    except Exception as e:
        raise RuntimeError(f"Failed to generate questions: {str(e)}")


async def generate_continuity_pack(brief: dict, answers: dict) -> dict:
    """
    Generate a continuity pack based on brief and Q&A answers.

    Args:
        brief: Brief intake data
        answers: Dict of question_id -> answer

    Returns:
        Continuity pack dict
    """
    logger.info(f"generate_continuity_pack called with MOCK_MODE={MOCK_MODE}")
    logger.info(f"Brief: {json.dumps(brief, indent=2)[:500]}")
    logger.info(f"Answers: {json.dumps(answers, indent=2)}")

    if MOCK_MODE:
        logger.info("Returning mock continuity pack due to MOCK_MODE=True")
        return get_mock_continuity_pack()

    system_prompt = """You are a professional video production designer. Create a comprehensive continuity pack for consistent video production.

The continuity pack must include:
1. anchors: Array of visual anchors with type (character, product, wardrobe, props, environment) and detailed description
2. lighting_recipe: Object with key_light, fill_light, rim_light, softness, time_of_day
3. palette_anchors: Array of 3-5 colors with name and hex code
4. do_list: Array of 5 production guidelines to follow
5. dont_list: Array of 5 things to avoid
6. style_clause: One sentence defining the overall visual style

Return valid JSON matching this structure exactly."""

    # Format Q&A for context
    qa_text = ""
    for qid, answer in answers.items():
        qa_text += f"Q: {qid}\nA: {answer}\n\n"

    user_prompt = f"""Brief:
Project: {brief.get('project_name', 'Untitled')}
Goal: {brief.get('goal', 'Not specified')}
Platform: {brief.get('platform', 'Not specified')}
Aspect Ratio: {brief.get('aspect_ratio', '16:9')}
Duration: {brief.get('duration_seconds', 12)} seconds
Brand Vibe: {', '.join(brief.get('brand_vibe', []))}
Avoid Vibe: {', '.join(brief.get('avoid_vibe', []))}
Subject: {brief.get('product_or_subject_description', 'Not provided')}

Clarifying Q&A:
{qa_text}

Create a detailed continuity pack for this video project."""

    try:
        logger.info("Calling OpenAI for continuity pack generation...")
        content = await asyncio.to_thread(
            _chat,
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        logger.info(f"OpenAI response (first 500 chars): {content[:500]}")

        result = _parse_json_response(content, "{}")
        logger.info(f"Parsed continuity pack keys: {list(result.keys()) if isinstance(result, dict) else 'not a dict'}")
        return result

    except Exception as e:
        logger.error(f"Failed to generate continuity pack: {str(e)}")
        raise RuntimeError(f"Failed to generate continuity pack: {str(e)}")


async def generate_shot_plan(brief: dict, continuity: dict) -> dict:
    """
    Generate a shot plan based on brief and continuity pack.

    Args:
        brief: Brief intake data
        continuity: Continuity pack data

    Returns:
        Shot plan dict with shots array
    """
    if MOCK_MODE:
        return get_mock_shot_plan()

    duration = brief.get("duration_seconds", 12)
    num_shots = min(8, max(4, duration // 3))  # 4-8 shots based on duration

    system_prompt = f"""You are a professional video director. Create a shot plan with {num_shots} shots for a {duration}-second video.

Each shot must include:
- id: UUID string
- shot_number: Integer (1-indexed)
- start_sec: Float (start time)
- end_sec: Float (end time)
- shot_type: One of "wide", "medium", "close", "detail"
- camera_move: One of "none", "pan", "tilt", "orbit", "push_in", "pull_out", "crane"
- framing_notes: Detailed framing description
- subject_action_beats: Array of 2-4 short action descriptions
- setting_notes: Setting/environment notes
- audio_cue: Audio/sound notes (or null)
- purpose: What this shot communicates

Rules:
- ONE primary camera move per shot
- Shots must cover 0 to {duration} seconds exactly
- Keep action beats countable and short (2-4 per shot)
- Balance shot types for visual variety
- Each shot should have a clear purpose

Return a JSON object with a "shots" array."""

    user_prompt = f"""Brief:
Project: {brief.get('project_name', 'Untitled')}
Goal: {brief.get('goal', 'Not specified')}
Platform: {brief.get('platform', 'Not specified')}
Subject: {brief.get('product_or_subject_description', 'Not provided')}
Must Include: {', '.join(brief.get('must_include', []))}

Continuity Pack:
Anchors: {json.dumps(continuity.get('anchors', []))}
Style: {continuity.get('style_clause', 'Not defined')}
Do List: {json.dumps(continuity.get('do_list', []))}

Create a {num_shots}-shot plan covering {duration} seconds."""

    try:
        content = await asyncio.to_thread(
            _chat,
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        result = _parse_json_response(content, '{"shots": []}')

        # Ensure each shot has a UUID
        for shot in result.get("shots", []):
            if "id" not in shot or not shot["id"]:
                shot["id"] = str(uuid.uuid4())

        return result

    except Exception as e:
        raise RuntimeError(f"Failed to generate shot plan: {str(e)}")


async def generate_prompt_pack(
    shots: list[dict],
    continuity: dict,
    brief: dict,
    target_model: str = "sora_2",
) -> dict:
    """
    Generate a prompt pack for all shots.

    This uses the compiler to generate prompts, with LLM enhancement.

    Args:
        shots: Shot plan shots array
        continuity: Continuity pack data
        brief: Brief intake data
        target_model: Target video generation model

    Returns:
        Prompt pack dict with target_model and prompts array
    """
    if MOCK_MODE:
        return get_mock_prompt_pack()

    # Use the compiler to generate base prompts
    prompt_pack = compile_all_shots(shots, continuity, brief, target_model)

    # Enhance the prompts with LLM
    try:
        prompt_pack = await _enhance_prompts_with_llm(prompt_pack, continuity, brief)
    except Exception as e:
        print(f"Error enhancing prompts: {e}")
        # Fall back to compiler-generated prompts

    return prompt_pack


async def _enhance_prompts_with_llm(
    prompt_pack: dict,
    continuity: dict,
    brief: dict,
) -> dict:
    """Enhance compiler-generated prompts with LLM refinement."""
    system_prompt = """You are a professional prompt engineer for AI video generation. Refine video prompts for clarity and effectiveness.

For each prompt, ensure:
1. Clear subject description
2. Specific camera framing and movement
3. Lighting details
4. Color palette guidance
5. Style and mood
6. Motion and pacing notes

Return the same JSON structure with improved prompt_text values."""

    user_prompt = f"""Continuity:
Style: {continuity.get('style_clause', '')}
Lighting: {json.dumps(continuity.get('lighting_recipe', {}))}
Palette: {json.dumps(continuity.get('palette_anchors', []))}

Brief:
Subject: {brief.get('product_or_subject_description', '')}
Vibe: {', '.join(brief.get('brand_vibe', []))}

Current Prompts:
{json.dumps(prompt_pack, indent=2)}

Enhance each prompt for better video generation results."""

    try:
        content = await asyncio.to_thread(
            _chat,
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        enhanced = _parse_json_response(content, "{}")
        # Validate that we got a proper prompt pack structure
        if enhanced and "prompts" in enhanced:
            return enhanced
        return prompt_pack

    except Exception as e:
        print(f"Error in LLM enhancement: {e}")
        return prompt_pack
