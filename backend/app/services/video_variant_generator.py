"""Video prompt variant generation service using LLM."""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any

# Add project root to path for llm imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from llm.client import chat

logger = logging.getLogger(__name__)

# Editable prompt template for variant generation
VARIANT_GENERATION_PROMPT = """You are an expert video prompt engineer. Your task is to generate creative variations of a video prompt while preserving its core intent.

Given the following structured video prompt, generate {count} unique variations that explore different creative directions while maintaining the essential purpose.

## Source Prompt

**Scene Description:**
{scene_description}

**Motion/Timing:**
{motion_timing}

**Style/Tone:**
{style_tone}

**Camera Language:**
{camera_language}

**Constraints:**
{constraints}

**Negative Instructions (what to avoid):**
{negative_instructions}

## Instructions

Generate {count} variations of this prompt. For each variation:
1. Keep the core subject/theme but explore different angles
2. Vary the visual style, mood, or atmosphere
3. Experiment with different camera movements or perspectives
4. Adjust timing and motion dynamics
5. Maintain or adapt the constraints appropriately

Return your response as a JSON array with {count} objects. Each object must have these exact fields:
- scene_description
- motion_timing
- style_tone
- camera_language
- constraints
- negative_instructions

Respond ONLY with the JSON array, no additional text.

Example format:
[
  {{
    "scene_description": "...",
    "motion_timing": "...",
    "style_tone": "...",
    "camera_language": "...",
    "constraints": "...",
    "negative_instructions": "..."
  }},
  ...
]"""


async def generate_prompt_variants(
    source_version: dict[str, Any],  # Dict with version fields
    count: int = 5,
) -> list[dict[str, str | None]]:
    """
    Generate prompt variants using LLM.

    Args:
        source_version: Dict containing version fields (scene_description, etc.)
        count: Number of variants to generate (1-10).

    Returns:
        List of variant dictionaries with structured fields.

    Raises:
        Exception: If LLM call fails or response parsing fails.
    """
    # Build the prompt
    prompt = VARIANT_GENERATION_PROMPT.format(
        count=count,
        scene_description=source_version.get("scene_description") or "(not specified)",
        motion_timing=source_version.get("motion_timing") or "(not specified)",
        style_tone=source_version.get("style_tone") or "(not specified)",
        camera_language=source_version.get("camera_language") or "(not specified)",
        constraints=source_version.get("constraints") or "(not specified)",
        negative_instructions=source_version.get("negative_instructions") or "(not specified)",
    )

    logger.info(f"Generating {count} variants for version {source_version.get('id')}")

    # Call the LLM in a thread pool to avoid blocking the async event loop
    def call_llm():
        return chat(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a video prompt engineering expert. Always respond with valid JSON."},
                {"role": "user", "content": prompt},
            ],
        )

    try:
        response = await asyncio.to_thread(call_llm)
    except NotImplementedError as e:
        logger.error(f"LLM not configured: {e}")
        raise Exception("LLM service not configured. Please set OPENAI_API_KEY.") from e
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise Exception(f"Failed to generate variants: {str(e)}") from e

    # Parse the response
    try:
        # Try to extract JSON from the response
        response_text = response.strip()

        # Handle case where response might be wrapped in markdown code blocks
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        variants = json.loads(response_text)

        if not isinstance(variants, list):
            raise ValueError("Response is not a JSON array")

        # Validate and normalize each variant
        normalized_variants = []
        expected_fields = [
            "scene_description",
            "motion_timing",
            "style_tone",
            "camera_language",
            "constraints",
            "negative_instructions",
        ]

        for variant in variants[:count]:  # Limit to requested count
            if not isinstance(variant, dict):
                continue

            normalized = {}
            for field in expected_fields:
                value = variant.get(field)
                # Normalize empty strings and None to None
                if value and isinstance(value, str) and value.strip() and value.strip().lower() != "(not specified)":
                    normalized[field] = value.strip()
                else:
                    normalized[field] = None

            normalized_variants.append(normalized)

        if not normalized_variants:
            raise ValueError("No valid variants in response")

        logger.info(f"Successfully generated {len(normalized_variants)} variants")
        return normalized_variants

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}")
        logger.error(f"Response was: {response[:500]}")
        raise Exception("Failed to parse variant response from LLM") from e
    except Exception as e:
        logger.error(f"Failed to process variants: {e}")
        raise Exception(f"Failed to process variants: {str(e)}") from e
