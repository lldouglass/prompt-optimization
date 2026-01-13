"""QA scoring algorithm for video workflows."""

import re
from typing import Optional

# Vague adjectives that increase ambiguity risk
VAGUE_ADJECTIVES = [
    "nice", "good", "interesting", "beautiful", "amazing", "great", "cool",
    "awesome", "wonderful", "fantastic", "pretty", "lovely", "perfect",
]

# Compound camera move indicators
COMPOUND_MOVE_PATTERNS = [
    r"\band\b",
    r"\+",
    r"\bwhile\b",
    r"\bwith\b.*\bmovement\b",
    r"\bcombined\b",
]


def calculate_ambiguity_risk(prompts: list[dict]) -> int:
    """
    Calculate ambiguity risk score (0-100, lower is better).

    Scoring rules:
    - +10 for each prompt < 50 characters
    - +15 for each vague adjective without anchor
    - +10 for missing camera move instruction
    - +10 for missing lighting reference
    - +20 for no subject described
    """
    if not prompts:
        return 100  # Maximum risk if no prompts

    total_risk = 0

    for prompt_data in prompts:
        prompt_text = prompt_data.get("prompt_text", "")
        prompt_lower = prompt_text.lower()

        # Check prompt length
        if len(prompt_text) < 50:
            total_risk += 10

        # Check for vague adjectives without specific anchors
        for adj in VAGUE_ADJECTIVES:
            if adj in prompt_lower:
                # Check if it's followed by specific details (has comma or period within 30 chars)
                idx = prompt_lower.find(adj)
                context = prompt_lower[idx:idx+50]
                if "," not in context and "." not in context:
                    total_risk += 5  # Reduced from 15 since we check each adjective

        # Check for camera move instruction
        camera_keywords = ["camera", "shot", "framing", "angle", "push", "pull", "pan", "tilt", "static", "locked"]
        has_camera = any(kw in prompt_lower for kw in camera_keywords)
        if not has_camera:
            total_risk += 10

        # Check for lighting reference
        lighting_keywords = ["light", "lighting", "lit", "illumin", "shadow", "bright", "dark", "glow", "sun", "window"]
        has_lighting = any(kw in prompt_lower for kw in lighting_keywords)
        if not has_lighting:
            total_risk += 10

        # Check for subject description
        subject_keywords = ["person", "man", "woman", "barista", "chef", "hands", "object", "product", "cup", "item"]
        has_subject = any(kw in prompt_lower for kw in subject_keywords)
        if not has_subject:
            total_risk += 20

    # Normalize to 0-100
    max_possible = len(prompts) * 55  # Maximum risk per prompt
    normalized = min(100, int((total_risk / max(max_possible, 1)) * 100))

    return normalized


def calculate_motion_complexity_risk(shots: list[dict]) -> int:
    """
    Calculate motion complexity risk score (0-100, lower is better).

    Scoring rules:
    - +20 for compound camera moves (contains "+" or "and")
    - +10 for each shot with > 4 action beats
    - +15 for duration < 2 seconds with movement
    - +10 for conflicting movements
    """
    if not shots:
        return 0  # No shots = no complexity risk

    total_risk = 0

    for shot in shots:
        camera_move = shot.get("camera_move", "none")
        framing_notes = shot.get("framing_notes", "")
        action_beats = shot.get("subject_action_beats", [])
        start_sec = shot.get("start_sec", 0)
        end_sec = shot.get("end_sec", 0)
        duration = end_sec - start_sec

        combined_text = f"{camera_move} {framing_notes}".lower()

        # Check for compound camera moves
        for pattern in COMPOUND_MOVE_PATTERNS:
            if re.search(pattern, combined_text):
                total_risk += 20
                break

        # Check for too many action beats
        if len(action_beats) > 4:
            total_risk += 10

        # Check for short duration with movement
        if duration < 2.0 and camera_move != "none":
            total_risk += 15

        # Check for conflicting movements
        conflicting_pairs = [
            ("push", "pull"),
            ("in", "out"),
            ("up", "down"),
            ("left", "right"),
        ]
        for pair in conflicting_pairs:
            if pair[0] in combined_text and pair[1] in combined_text:
                total_risk += 10
                break

    # Normalize to 0-100
    max_possible = len(shots) * 55  # Maximum risk per shot
    normalized = min(100, int((total_risk / max(max_possible, 1)) * 100))

    return normalized


def calculate_continuity_completeness(continuity: Optional[dict]) -> int:
    """
    Calculate continuity completeness score (0-100, higher is better).

    Scoring rules:
    - +20 for having anchors defined
    - +20 for having lighting recipe
    - +20 for having palette (3+ colors)
    - +20 for having do list (3+ items)
    - +20 for having style clause
    """
    if not continuity:
        return 0

    score = 0

    # Check anchors
    anchors = continuity.get("anchors", [])
    if anchors and len(anchors) >= 1:
        score += 20

    # Check lighting recipe
    lighting = continuity.get("lighting_recipe")
    if lighting and lighting.get("key_light"):
        score += 20

    # Check palette
    palette = continuity.get("palette_anchors", [])
    if palette and len(palette) >= 3:
        score += 20

    # Check do list
    do_list = continuity.get("do_list", [])
    if do_list and len(do_list) >= 3:
        score += 20

    # Check style clause
    style_clause = continuity.get("style_clause")
    if style_clause and len(style_clause) > 10:
        score += 20

    return score


def calculate_audio_readiness(shots: list[dict], brief: Optional[dict] = None) -> int:
    """
    Calculate audio readiness score (0-100, higher is better).

    Scoring rules:
    - Start at 100 if no dialogue expected
    - -20 for each shot missing audio_cue when audio is expected
    - -30 if dialogue chosen but no dialogue_block in prompts
    """
    if not shots:
        return 100

    # Check if dialogue/audio is expected from brief
    has_script = brief and brief.get("script_or_vo")

    score = 100

    # Count shots without audio cues
    shots_without_audio = sum(1 for shot in shots if not shot.get("audio_cue"))

    # Deduct points for missing audio cues (but not all shots need them)
    if shots_without_audio > len(shots) / 2:
        score -= min(40, shots_without_audio * 10)

    # If script/VO is present, we expect more audio readiness
    if has_script:
        # More strict scoring when dialogue is expected
        if shots_without_audio > 0:
            score -= min(30, shots_without_audio * 15)

    return max(0, score)


def calculate_overall_score(
    ambiguity_risk: int,
    motion_complexity_risk: int,
    continuity_completeness: int,
    audio_readiness: int,
) -> int:
    """
    Calculate overall QA score (0-100, higher is better).

    Weighted formula:
    = 100 - (0.30 * ambiguity_risk)
          - (0.25 * motion_complexity_risk)
          + (0.30 * continuity_completeness)
          + (0.15 * audio_readiness)

    Then normalized to 0-100 range.
    """
    # Start with base
    score = 100.0

    # Subtract risks (these are bad when high)
    score -= 0.30 * ambiguity_risk
    score -= 0.25 * motion_complexity_risk

    # Add completeness scores (these are good when high, but we need to scale)
    # Continuity completeness contributes positively
    score += 0.30 * (continuity_completeness - 50)  # Center around 50

    # Audio readiness contributes positively
    score += 0.15 * (audio_readiness - 50)  # Center around 50

    # Normalize to 0-100
    return max(0, min(100, int(score)))


def generate_warnings(
    shots: list[dict],
    prompts: list[dict],
    continuity: Optional[dict],
    brief: Optional[dict],
) -> list[str]:
    """Generate warning messages based on workflow analysis."""
    warnings = []

    # Check for shots with many action beats
    for i, shot in enumerate(shots, 1):
        beats = shot.get("subject_action_beats", [])
        if len(beats) > 3:
            warnings.append(f"Shot {i} has {len(beats)} action beats - consider simplifying for cleaner execution")

    # Check for missing continuity elements
    if continuity:
        if not continuity.get("lighting_recipe"):
            warnings.append("Lighting recipe is not defined - this may lead to inconsistent visuals")
        if len(continuity.get("palette_anchors", [])) < 3:
            warnings.append("Color palette has fewer than 3 anchors - consider adding more for consistency")

    # Check for short shots
    for i, shot in enumerate(shots, 1):
        duration = shot.get("end_sec", 0) - shot.get("start_sec", 0)
        if duration < 2.0:
            warnings.append(f"Shot {i} is only {duration:.1f}s - very short shots can feel rushed")

    # Check for audio consistency
    audio_cue_count = sum(1 for shot in shots if shot.get("audio_cue"))
    if 0 < audio_cue_count < len(shots):
        warnings.append(f"Only {audio_cue_count}/{len(shots)} shots have audio cues - consider adding to all or none")

    # Check for dialogue blocks if script present
    has_script = brief and brief.get("script_or_vo")
    has_dialogue = any(p.get("dialogue_block") for p in prompts)
    if has_script and not has_dialogue:
        warnings.append("Script/VO is provided but no dialogue blocks in prompts - add dialogue blocks for clarity")

    return warnings


def generate_fixes(
    shots: list[dict],
    prompts: list[dict],
    continuity: Optional[dict],
) -> list[dict]:
    """Generate suggested fixes for identified issues."""
    fixes = []

    # Check for compound camera moves
    for i, shot in enumerate(shots, 1):
        camera_move = shot.get("camera_move", "none")
        framing_notes = shot.get("framing_notes", "")
        combined = f"{camera_move} {framing_notes}".lower()

        if "and" in combined or "+" in combined or "while" in combined:
            fixes.append({
                "issue": f"Shot {i} has compound camera movement which may be difficult to execute",
                "fix": "Consider using a single camera movement or breaking into multiple shots"
            })

    # Check for missing anchors
    if continuity:
        if not continuity.get("anchors"):
            fixes.append({
                "issue": "No visual anchors defined in continuity pack",
                "fix": "Add character, product, and environment anchors for consistent visuals"
            })

    # Check for vague prompts
    for i, prompt in enumerate(prompts, 1):
        text = prompt.get("prompt_text", "")
        for adj in VAGUE_ADJECTIVES:
            if adj in text.lower():
                fixes.append({
                    "issue": f"Prompt {i} contains vague adjective '{adj}'",
                    "fix": f"Replace '{adj}' with specific, measurable descriptions"
                })
                break  # Only one fix per prompt for vague adjectives

    return fixes


def score_workflow(
    brief: Optional[dict],
    continuity: Optional[dict],
    shots: list[dict],
    prompts: list[dict],
) -> dict:
    """
    Run complete QA scoring on a workflow.

    Returns a dict with all scores, warnings, and fixes.
    """
    # Calculate individual scores
    ambiguity = calculate_ambiguity_risk(prompts)
    motion = calculate_motion_complexity_risk(shots)
    completeness = calculate_continuity_completeness(continuity)
    audio = calculate_audio_readiness(shots, brief)
    overall = calculate_overall_score(ambiguity, motion, completeness, audio)

    # Generate feedback
    warnings = generate_warnings(shots, prompts, continuity, brief)
    fixes = generate_fixes(shots, prompts, continuity)

    # Generate recommended questions based on gaps
    recommended_questions = []
    if not continuity or not continuity.get("lighting_recipe"):
        recommended_questions.append("What lighting style works best for your brand?")
    if len(prompts) > 0 and not any(p.get("dialogue_block") for p in prompts):
        recommended_questions.append("Would you like to add dialogue or voiceover to any shots?")
    if brief and not brief.get("reference_images"):
        recommended_questions.append("Do you have any reference images or videos to share?")

    return {
        "ambiguity_risk": ambiguity,
        "motion_complexity_risk": motion,
        "continuity_completeness": completeness,
        "audio_readiness": audio,
        "overall_score": overall,
        "warnings": warnings,
        "fixes": fixes,
        "recommended_questions": recommended_questions,
    }
