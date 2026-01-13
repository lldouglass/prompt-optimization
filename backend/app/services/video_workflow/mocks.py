"""Mock data for video workflow development and testing."""

import os
import uuid

# Check if mock mode is enabled via environment variable
MOCK_MODE = os.getenv("VIDEO_WORKFLOW_MOCK_MODE", "false").lower() == "true"


def get_mock_workflow_data() -> dict:
    """Get complete mock workflow data for the coffee shop promo example."""
    return {
        "brief": MOCK_BRIEF,
        "clarifying_questions": MOCK_CLARIFYING_QUESTIONS,
        "continuity_pack": MOCK_CONTINUITY_PACK,
        "shot_plan": MOCK_SHOT_PLAN,
        "prompt_pack": MOCK_PROMPT_PACK,
        "qa_score": MOCK_QA_SCORE,
    }


# ============================================================================
# Mock Brief (Steps 1-2)
# ============================================================================

MOCK_BRIEF = {
    "project_name": "Artisan Coffee Shop Promo",
    "goal": "product_ad",
    "platform": "instagram",
    "aspect_ratio": "9:16",
    "duration_seconds": 15,
    "brand_vibe": ["warm", "artisan", "cozy"],
    "avoid_vibe": ["corporate", "cold", "rushed"],
    "must_include": ["pour-over process", "steam rising", "brand logo on cup"],
    "must_avoid": ["cluttered backgrounds", "harsh lighting", "fast cuts"],
    "script_or_vo": None,
    "product_or_subject_description": "Local artisan coffee shop showcasing the pour-over brewing process. Focus on the craft and care that goes into each cup. The barista is skilled and passionate.",
    "reference_images": None,
    "clarifying_questions": [],
}


MOCK_CLARIFYING_QUESTIONS = [
    {
        "id": str(uuid.uuid4()),
        "question": "What shot style do you prefer for this video?",
        "category": "shot_style",
        "answer": "handheld with subtle movement for organic feel",
    },
    {
        "id": str(uuid.uuid4()),
        "question": "What pacing works best for your brand?",
        "category": "pacing",
        "answer": "smooth and cinematic, not too fast",
    },
    {
        "id": str(uuid.uuid4()),
        "question": "Should there be a primary camera movement throughout?",
        "category": "camera_movement",
        "answer": "gentle push-ins to draw attention to details",
    },
    {
        "id": str(uuid.uuid4()),
        "question": "What are the key action beats you want to capture?",
        "category": "action_beats",
        "answer": "1) kettle pouring, 2) coffee blooming, 3) steam rising, 4) final pour into cup",
    },
    {
        "id": str(uuid.uuid4()),
        "question": "What audio approach works for this video?",
        "category": "audio",
        "answer": "ambient coffee shop sounds with subtle background music",
    },
]


# ============================================================================
# Mock Continuity Pack (Step 3)
# ============================================================================

MOCK_CONTINUITY_PACK = {
    "anchors": [
        {"type": "character", "description": "Barista wearing cream linen apron over black shirt, visible tattoos on forearms, focused expression"},
        {"type": "product", "description": "Copper gooseneck kettle with wooden handle, Chemex glass pour-over brewer"},
        {"type": "environment", "description": "Wooden counter with warm wood grain, exposed brick wall in background, morning light from left window"},
        {"type": "props", "description": "White ceramic cup with embossed logo, freshly ground coffee in glass container"},
    ],
    "lighting_recipe": {
        "key_light": "Natural window light from camera left, soft and diffused through sheer curtains",
        "fill_light": "Ambient bounce from cream-colored walls",
        "rim_light": "Subtle warm backlight from pendant lamp, creates steam glow",
        "softness": "Very soft, no harsh shadows",
        "time_of_day": "Mid-morning, golden hour quality",
    },
    "palette_anchors": [
        {"name": "Espresso Brown", "hex": "#3D2314"},
        {"name": "Latte Cream", "hex": "#D4A574"},
        {"name": "Natural Cream", "hex": "#F5F5DC"},
        {"name": "Copper Accent", "hex": "#B87333"},
        {"name": "Warm Wood", "hex": "#8B4513"},
    ],
    "do_list": [
        "Keep camera movements slow and intentional",
        "Emphasize steam and liquid motion",
        "Show hands and craft in detail",
        "Maintain warm color temperature throughout",
        "Use shallow depth of field for intimate feel",
    ],
    "dont_list": [
        "No abrupt camera movements or fast pans",
        "Avoid showing cluttered or messy areas",
        "No harsh overhead lighting",
        "Don't cut away during key pour moments",
        "Avoid blue or cool color casts",
    ],
    "style_clause": "Intimate, warm, and tactile - capturing the meditative ritual of craft coffee preparation with a cinematic quality that feels both aspirational and authentic.",
}


# ============================================================================
# Mock Shot Plan (Step 4)
# ============================================================================

MOCK_SHOT_PLAN = {
    "shots": [
        {
            "id": str(uuid.uuid4()),
            "shot_number": 1,
            "start_sec": 0.0,
            "end_sec": 4.0,
            "shot_type": "wide",
            "camera_move": "push_in",
            "framing_notes": "Wide establishing shot of the coffee bar. Barista centered, brewing station visible. Camera slowly pushes in from medium-wide to medium.",
            "subject_action_beats": [
                "Barista prepares brewing station",
                "Reaches for copper kettle",
            ],
            "setting_notes": "Morning light streaming through left window. Exposed brick and wooden shelves visible in background.",
            "audio_cue": "Ambient coffee shop sounds, gentle background music fades in",
            "purpose": "Establish setting and mood, introduce the barista and craft environment",
        },
        {
            "id": str(uuid.uuid4()),
            "shot_number": 2,
            "start_sec": 4.0,
            "end_sec": 8.0,
            "shot_type": "close",
            "camera_move": "none",
            "framing_notes": "Close-up of barista's hands holding copper kettle, beginning the pour over the Chemex. Steam rises into frame.",
            "subject_action_beats": [
                "Kettle tips and water begins to pour",
                "Coffee grounds bloom as water hits",
                "Circular pour motion begins",
            ],
            "setting_notes": "Shallow depth of field, wooden counter surface visible at bottom of frame.",
            "audio_cue": "Sound of water pouring, coffee bubbling",
            "purpose": "Highlight the craft and precision of pour-over technique",
        },
        {
            "id": str(uuid.uuid4()),
            "shot_number": 3,
            "start_sec": 8.0,
            "end_sec": 12.0,
            "shot_type": "medium",
            "camera_move": "tilt",
            "framing_notes": "Medium shot focusing on Chemex. Camera slowly tilts up following the steam rising from the brewer.",
            "subject_action_beats": [
                "Steam rises dramatically",
                "Coffee drips into carafe below",
                "Barista's hands visible at top of frame",
            ],
            "setting_notes": "Backlit steam creates ethereal glow. Warm pendant light visible in upper background.",
            "audio_cue": "Coffee dripping, ambient sounds continue",
            "purpose": "Create visual poetry with steam, emphasize the sensory experience",
        },
        {
            "id": str(uuid.uuid4()),
            "shot_number": 4,
            "start_sec": 12.0,
            "end_sec": 15.0,
            "shot_type": "detail",
            "camera_move": "push_in",
            "framing_notes": "Detail shot of white ceramic cup with embossed logo. Camera pushes in slowly as coffee is poured into cup.",
            "subject_action_beats": [
                "Coffee pours into cup",
                "Cup fills, steam rises",
                "Final moment holds on logo",
            ],
            "setting_notes": "Clean composition, cup centered on wooden surface. Soft morning light.",
            "audio_cue": "Pour sound, music swells subtly to end",
            "purpose": "Product reveal with brand logo, satisfying conclusion",
        },
    ]
}


# ============================================================================
# Mock Prompt Pack (Step 5)
# ============================================================================

MOCK_PROMPT_PACK = {
    "target_model": "sora_2",
    "prompts": [
        {
            "shot_id": MOCK_SHOT_PLAN["shots"][0]["id"],
            "sora_params": {
                "resolution": "1080p",
                "duration": 4.0,
                "aspect_ratio": "9:16",
                "fps": 24,
            },
            "prompt_text": """Wide establishing shot of an artisan coffee bar interior. A barista wearing a cream linen apron over a black shirt stands centered behind a wooden counter with warm wood grain. Exposed brick wall visible in background. Morning light streams through a window on the left side, creating soft, diffused illumination.

Camera slowly pushes in from medium-wide to medium framing over 4 seconds.

The barista, focused and professional with visible forearm tattoos, prepares a brewing station and reaches for a copper gooseneck kettle with wooden handle. A Chemex glass pour-over brewer sits on the counter.

Color palette: warm espresso browns, latte cream tones, natural wood colors. Very soft lighting with no harsh shadows. Cinematic quality, intimate and authentic atmosphere.

Style: Smooth, intentional camera movement. Shallow depth of field creates intimate feel.""",
            "negative_prompt_text": "harsh lighting, cluttered background, fast movement, cold colors, blue tones, corporate aesthetic, rushed motion, abrupt camera moves",
            "dialogue_block": None,
        },
        {
            "shot_id": MOCK_SHOT_PLAN["shots"][1]["id"],
            "sora_params": {
                "resolution": "1080p",
                "duration": 4.0,
                "aspect_ratio": "9:16",
                "fps": 24,
            },
            "prompt_text": """Close-up shot of skilled barista hands holding a copper gooseneck kettle with wooden handle. The hands pour water in a slow, controlled circular motion over coffee grounds in a Chemex glass brewer.

Static camera, locked off. Shallow depth of field with wooden counter surface visible at bottom of frame.

As water hits the grounds, coffee blooms beautifully - grounds rise and bubble. Steam rises into the frame, catching warm backlight from a pendant lamp.

Color palette: copper accent tones, espresso brown, latte cream. Warm color temperature throughout. Soft, diffused lighting from natural window light on the left.

Style: Intimate, tactile, meditative. Focus on the craft and precision of the pour-over technique.""",
            "negative_prompt_text": "harsh lighting, fast motion, shaky camera, cold colors, blue tones, cluttered frame, harsh shadows",
            "dialogue_block": None,
        },
        {
            "shot_id": MOCK_SHOT_PLAN["shots"][2]["id"],
            "sora_params": {
                "resolution": "1080p",
                "duration": 4.0,
                "aspect_ratio": "9:16",
                "fps": 24,
            },
            "prompt_text": """Medium shot centered on a Chemex glass pour-over coffee brewer on a wooden counter. Steam rises dramatically from the brewer, backlit by a warm pendant lamp creating an ethereal glow.

Camera slowly tilts upward following the rising steam over 4 seconds.

Coffee drips into the glass carafe below. Barista's hands wearing cream apron visible at top of frame. Exposed brick wall softly blurred in background.

Color palette: warm espresso browns, copper accents, cream tones. Golden hour quality lighting, very soft with no harsh shadows.

Style: Visual poetry with steam. Sensory and atmospheric. Cinematic quality that feels aspirational yet authentic.""",
            "negative_prompt_text": "abrupt camera movement, harsh lighting, cold blue tones, cluttered background, fast cuts, shaky footage",
            "dialogue_block": None,
        },
        {
            "shot_id": MOCK_SHOT_PLAN["shots"][3]["id"],
            "sora_params": {
                "resolution": "1080p",
                "duration": 3.0,
                "aspect_ratio": "9:16",
                "fps": 24,
            },
            "prompt_text": """Detail shot of a white ceramic coffee cup with embossed logo centered on a wooden surface. Clean composition with soft morning light from the left.

Camera slowly pushes in toward the cup over 3 seconds.

Fresh brewed coffee is poured into the cup, filling it. Steam rises gently from the hot coffee. The final moment holds on the brand logo visible on the cup.

Color palette: natural cream, warm wood tones, espresso brown liquid. Warm color temperature, soft diffused lighting.

Style: Product reveal moment. Satisfying conclusion. Intimate and warm. Shallow depth of field keeps focus on the cup.""",
            "negative_prompt_text": "harsh overhead lighting, cold colors, cluttered background, fast pour, abrupt ending, blue tones",
            "dialogue_block": None,
        },
    ]
}


# ============================================================================
# Mock QA Score (Step 6)
# ============================================================================

MOCK_QA_SCORE = {
    "ambiguity_risk": 15,
    "motion_complexity_risk": 20,
    "continuity_completeness": 95,
    "audio_readiness": 80,
    "overall_score": 84,
    "warnings": [
        "Shot 2 has 3 action beats - consider simplifying for cleaner execution",
        "Audio cues are present but no dialogue blocks defined - confirm this is intentional",
    ],
    "fixes": [
        {
            "issue": "Shot 3 tilt movement combined with steam tracking may be complex",
            "fix": "Consider using a static shot with steam as the only motion element"
        },
    ],
    "recommended_questions": [
        "Would you like to add background music specifications?",
        "Should we define specific coffee brand elements for the logo shot?",
    ],
}


# ============================================================================
# Individual Mock Generators (for step-by-step generation)
# ============================================================================

def get_mock_clarifying_questions() -> list[dict]:
    """Return mock clarifying questions."""
    return MOCK_CLARIFYING_QUESTIONS


def get_mock_continuity_pack() -> dict:
    """Return mock continuity pack."""
    return MOCK_CONTINUITY_PACK


def get_mock_shot_plan() -> dict:
    """Return mock shot plan."""
    return MOCK_SHOT_PLAN


def get_mock_prompt_pack() -> dict:
    """Return mock prompt pack."""
    return MOCK_PROMPT_PACK


def get_mock_qa_score() -> dict:
    """Return mock QA score."""
    return MOCK_QA_SCORE
