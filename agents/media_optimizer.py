"""
Media Prompt Optimizer Agent - Generates and optimizes prompts for photo and video AI models.

Uses best practices from research on Midjourney, Stable Diffusion, Firefly, Runway, Veo, Luma, and Kling
to create high-quality prompts for visual media generation.
"""

import json
from dataclasses import dataclass, field
from typing import Optional, List, Literal

import llm.client as llm_client


class MediaOptimizerError(Exception):
    pass


# ============================================================================
# PHOTO PROMPT SYSTEM PROMPTS
# ============================================================================

PHOTO_OPTIMIZER_SYSTEM_PROMPT = """You are an expert prompt engineer specializing in AI image generation and photo enhancement.

You create optimized prompts following the "Subject → Style → Technical → Constraints" pattern used by professionals.

## BEST PRACTICES FOR PHOTO PROMPTS

1. **Subject Definition** (Most Important)
   - Lead with the main subject clearly described
   - Include relevant context (setting, environment)
   - Be specific about what's in the image

2. **Style & Lighting**
   - Specify lighting conditions (warm tungsten, soft diffused, dramatic shadows)
   - Include artistic style (cinematic, editorial, documentary)
   - Define mood and atmosphere

3. **Technical Specifications**
   - Camera/lens suggestions (shallow depth of field, wide angle)
   - Quality keywords (sharp focus, detailed, high resolution)
   - Color grading (warm tones, muted colors, vibrant)

4. **Corrections** (for enhancement prompts)
   - Low light: "reduced noise, clean shadows, natural detail"
   - Backlit: "balanced exposure, recovered highlights, no haloing"
   - Color cast: "neutral white balance, consistent skin tones"
   - Motion blur: "sharp edges, crisp detail, natural texture"
   - Compression: "remove artifacts, smooth gradients, preserved detail"

5. **Constraints**
   - What must NOT change (preserve identity, keep brand colors)
   - What to avoid (no text, no watermarks, no extra elements)

## OUTPUT RULES
- Write descriptive statements, NOT commands
- Keep style coherent (don't mix "realistic" with "cartoon")
- Be specific but don't overstuff (aim for 30-80 words)
- Put the most important elements first

Return ONLY a valid JSON object:
{
  "optimized_prompt": "the full optimized prompt",
  "improvements": ["specific improvement 1", "specific improvement 2", ...],
  "reasoning": "2-3 sentences explaining why these changes will improve results",
  "tips": ["tip 1 for this specific prompt", "tip 2", ...]
}
"""

PHOTO_SCORER_SYSTEM_PROMPT = """You are a HARSH prompt quality evaluator for AI image generation prompts.

Score the prompt on a 100-point scale, then normalize to 0-10.

## SCORING RUBRIC

1. **Subject Clarity** (0-25 points)
   - 0: No clear subject or extremely vague
   - 10: Subject mentioned but poorly defined
   - 20: Clear subject with some context
   - 25: Crystal clear subject with specific details and context

2. **Style & Lighting** (0-20 points)
   - 0: No style or lighting mentioned
   - 10: Generic style terms (beautiful, nice)
   - 15: Specific style OR lighting
   - 20: Both specific style AND lighting defined

3. **Technical Specifications** (0-20 points)
   - 0: No technical details
   - 10: Basic quality terms only
   - 15: Some camera/lens or quality specs
   - 20: Well-defined technical parameters

4. **Structure & Organization** (0-15 points)
   - 0: Chaotic, contradictory, or overstuffed
   - 8: Readable but poorly organized
   - 12: Well-organized with clear flow
   - 15: Excellent structure, prioritized elements

5. **Constraint Clarity** (0-10 points)
   - 0: No constraints or boundaries
   - 5: Some constraints mentioned
   - 10: Clear constraints and what to preserve/avoid

6. **Coherence** (0-10 points)
   - 0: Conflicting styles or impossible combinations
   - 5: Minor inconsistencies
   - 10: Fully coherent, all elements work together

## SCORING PHILOSOPHY
- Most prompts should score 30-50 (needs work)
- 60-75 is good but improvable
- 80+ is rare and only for excellent prompts
- Be harsh but fair

Return ONLY a valid JSON object:
{
  "score": <number 0-100>,
  "breakdown": {
    "subject_clarity": <0-25>,
    "style_lighting": <0-20>,
    "technical_specs": <0-20>,
    "structure": <0-15>,
    "constraints": <0-10>,
    "coherence": <0-10>
  },
  "critique": "1-2 sentences on main issues"
}
"""

# ============================================================================
# VIDEO PROMPT SYSTEM PROMPTS
# ============================================================================

VIDEO_OPTIMIZER_SYSTEM_PROMPT = """You are an expert prompt engineer specializing in AI video generation (Runway, Veo, Luma, Kling).

You create optimized prompts following the "[Camera/Shot] + [Scene] + [Subject] + [Action] + [Lighting] + [Style]" pattern.

## BEST PRACTICES FOR VIDEO PROMPTS

1. **Camera & Shot** (Start with this)
   - Shot type: wide, medium, close-up, extreme close-up, over-the-shoulder
   - Camera movement: dolly in/out, pan left/right, tracking, crane, orbit, handheld, POV, static
   - Movement speed: slow, medium, fast
   - Example: "Slow dolly-in, medium close-up"

2. **Scene Description**
   - Setting and environment
   - Time of day, weather, atmosphere
   - Example: "steamy kitchen at night"

3. **Subject & Action**
   - Who/what is the focus
   - What they're doing (use present tense)
   - Example: "chef plates ramen, hands move precisely"

4. **Lighting & Style**
   - Lighting type: tungsten, natural, dramatic, soft, harsh
   - Visual style: cinematic, documentary, commercial, film noir
   - Color grading: warm tones, cool tones, desaturated
   - Example: "warm tungsten lighting, shallow depth of field, cinematic"

5. **Motion Endpoints** (Critical for video!)
   - Where movement STARTS and ENDS
   - Prevents camera drift and chaos
   - Example: "push-in then settles on subject's face"

## CRITICAL RULES
- Use POSITIVE phrasing only (no "don't" or "no" or "avoid")
- Specify motion endpoints to prevent drift
- Keep prompts focused (40-100 words ideal)
- Use cinematography terminology precisely

Return ONLY a valid JSON object:
{
  "optimized_prompt": "the full optimized prompt",
  "improvements": ["specific improvement 1", "specific improvement 2", ...],
  "reasoning": "2-3 sentences explaining why these changes will improve results",
  "tips": ["tip 1 for this specific prompt", "tip 2", ...]
}
"""

VIDEO_SCORER_SYSTEM_PROMPT = """You are a HARSH prompt quality evaluator for AI video generation prompts.

Score the prompt on a 100-point scale, then normalize to 0-10.

## SCORING RUBRIC

1. **Camera & Shot Specification** (0-25 points)
   - 0: No camera/shot info
   - 10: Vague camera reference ("camera moves")
   - 18: Shot type OR movement specified
   - 25: Both shot type AND movement with speed/direction

2. **Scene & Subject Clarity** (0-20 points)
   - 0: No clear scene or subject
   - 10: Basic scene/subject mentioned
   - 15: Clear scene with context
   - 20: Vivid scene with specific subject and action

3. **Motion Description** (0-20 points)
   - 0: No motion or action described
   - 10: Basic action mentioned
   - 15: Clear action with some motion detail
   - 20: Precise motion with timing and flow

4. **Motion Endpoints** (0-15 points)
   - 0: No endpoints, movement undefined
   - 8: Partial endpoint (start OR end)
   - 15: Clear start AND end of movement

5. **Style & Lighting** (0-10 points)
   - 0: No style or lighting
   - 5: Basic style OR lighting
   - 10: Both specific style AND lighting

6. **Prompt Hygiene** (0-10 points)
   - 0: Negative phrasing, contradictions, overstuffed
   - 5: Minor issues
   - 10: Clean, positive phrasing, coherent

## SCORING PHILOSOPHY
- Most prompts should score 30-50 (needs work)
- 60-75 is good but improvable
- 80+ is rare and only for excellent prompts

Return ONLY a valid JSON object:
{
  "score": <number 0-100>,
  "breakdown": {
    "camera_shot": <0-25>,
    "scene_subject": <0-20>,
    "motion": <0-20>,
    "motion_endpoints": <0-15>,
    "style_lighting": <0-10>,
    "prompt_hygiene": <0-10>
  },
  "critique": "1-2 sentences on main issues"
}
"""


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class MediaAnalysis:
    """Analysis of a media prompt's quality."""
    score: float  # 0-10 normalized score
    breakdown: dict  # Category scores
    critique: str
    media_type: Literal["photo", "video"]


@dataclass
class MediaOptimizationResult:
    """Result of media prompt optimization."""
    optimized_prompt: str
    original_prompt: Optional[str]  # Only if existing prompt was provided
    original_score: Optional[float]  # Only if existing prompt was provided
    optimized_score: float
    improvements: List[str]
    reasoning: str
    tips: List[str]
    media_type: Literal["photo", "video"]


# ============================================================================
# MEDIA OPTIMIZER CLASS
# ============================================================================

class MediaOptimizer:
    """Optimizes prompts for photo and video AI generation."""

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model

    def score_prompt(
        self,
        prompt: str,
        media_type: Literal["photo", "video"]
    ) -> MediaAnalysis:
        """Score a prompt on a 0-10 scale."""

        system_prompt = (
            PHOTO_SCORER_SYSTEM_PROMPT if media_type == "photo"
            else VIDEO_SCORER_SYSTEM_PROMPT
        )

        user_message = f"Score this {media_type} prompt:\n\n{prompt}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        response = llm_client.chat(self.model, messages)

        try:
            result = json.loads(response)
            # Normalize 0-100 to 0-10
            normalized_score = result["score"] / 10
            return MediaAnalysis(
                score=round(normalized_score, 1),
                breakdown=result["breakdown"],
                critique=result["critique"],
                media_type=media_type,
            )
        except (json.JSONDecodeError, KeyError) as e:
            raise MediaOptimizerError(f"Failed to parse scoring response: {e}")

    def generate_prompt(
        self,
        media_type: Literal["photo", "video"],
        subject: str,
        style_lighting: str = "",
        # Photo-specific
        issues_to_fix: Optional[List[str]] = None,
        constraints: str = "",
        # Video-specific
        camera_movement: str = "",
        shot_type: str = "",
        motion_endpoints: str = "",
        # Optional existing prompt to improve
        existing_prompt: str = "",
    ) -> MediaOptimizationResult:
        """Generate or optimize a media prompt."""

        # Build context for the optimizer
        context_parts = []

        if existing_prompt:
            context_parts.append(f"EXISTING PROMPT TO IMPROVE:\n{existing_prompt}")

        context_parts.append(f"SUBJECT: {subject}")

        if style_lighting:
            context_parts.append(f"STYLE & LIGHTING: {style_lighting}")

        if media_type == "photo":
            if issues_to_fix:
                context_parts.append(f"ISSUES TO FIX: {', '.join(issues_to_fix)}")
            if constraints:
                context_parts.append(f"CONSTRAINTS (must preserve): {constraints}")
        else:  # video
            if camera_movement:
                context_parts.append(f"CAMERA MOVEMENT: {camera_movement}")
            if shot_type:
                context_parts.append(f"SHOT TYPE: {shot_type}")
            if motion_endpoints:
                context_parts.append(f"MOTION ENDPOINTS: {motion_endpoints}")

        context = "\n\n".join(context_parts)

        system_prompt = (
            PHOTO_OPTIMIZER_SYSTEM_PROMPT if media_type == "photo"
            else VIDEO_OPTIMIZER_SYSTEM_PROMPT
        )

        user_message = f"""Generate an optimized {media_type} prompt based on these inputs:

{context}

{"Improve the existing prompt while preserving its intent." if existing_prompt else "Generate a new prompt from scratch."}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        response = llm_client.chat(self.model, messages)

        try:
            result = json.loads(response)
        except json.JSONDecodeError as e:
            raise MediaOptimizerError(f"Failed to parse optimizer response: {e}")

        # Score the optimized prompt
        optimized_analysis = self.score_prompt(result["optimized_prompt"], media_type)

        # If there was an existing prompt, score it too
        original_score = None
        if existing_prompt:
            original_analysis = self.score_prompt(existing_prompt, media_type)
            original_score = original_analysis.score

        return MediaOptimizationResult(
            optimized_prompt=result["optimized_prompt"],
            original_prompt=existing_prompt if existing_prompt else None,
            original_score=original_score,
            optimized_score=optimized_analysis.score,
            improvements=result.get("improvements", []),
            reasoning=result.get("reasoning", ""),
            tips=result.get("tips", []),
            media_type=media_type,
        )
