"""Prompt compilers for different video generation models."""

from abc import ABC, abstractmethod
from typing import Optional


class BasePromptCompiler(ABC):
    """Base class for video prompt compilers."""

    @abstractmethod
    def compile_shot(self, shot: dict, continuity: dict, brief: dict) -> dict:
        """Compile a single shot into model-specific format."""
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Return the model name this compiler targets."""
        pass


class Sora2Compiler(BasePromptCompiler):
    """
    Compiles prompts for OpenAI Sora 2.

    Output format:
    - Main prompt (positive, descriptive)
    - Separate parameters for API call
    - Optional dialogue/audio track
    """

    def get_model_name(self) -> str:
        return "sora_2"

    def compile_shot(self, shot: dict, continuity: dict, brief: dict) -> dict:
        """
        Compile a single shot into Sora 2 format.

        Args:
            shot: Shot data from shot plan
            continuity: Continuity pack data
            brief: Brief intake data

        Returns:
            Dict with shot_id, sora_params, prompt_text, dialogue_block
        """
        # Build the main prompt text (includes exclusions woven in)
        prompt_text = self._build_prompt_text(shot, continuity, brief)

        # Get Sora-specific parameters
        sora_params = self._get_sora_params(shot, brief)

        # Extract dialogue if present
        dialogue_block = self._extract_dialogue(shot, brief)

        return {
            "shot_id": shot.get("id", ""),
            "sora_params": sora_params,
            "prompt_text": prompt_text,
            "dialogue_block": dialogue_block,
        }

    def _build_prompt_text(self, shot: dict, continuity: dict, brief: dict) -> str:
        """Build the main prompt text for a shot."""
        parts = []

        # 1. Shot description (type and framing)
        shot_type = shot.get("shot_type", "medium")
        framing = shot.get("framing_notes", "")
        parts.append(f"{shot_type.title()} shot. {framing}")

        # 2. Camera movement
        camera_move = shot.get("camera_move", "none")
        duration = shot.get("end_sec", 0) - shot.get("start_sec", 0)
        if camera_move != "none":
            move_desc = self._describe_camera_move(camera_move, duration)
            parts.append(move_desc)

        # 3. Subject and action
        action_beats = shot.get("subject_action_beats", [])
        if action_beats:
            action_text = self._describe_actions(action_beats, continuity)
            parts.append(action_text)

        # 4. Setting notes
        setting = shot.get("setting_notes", "")
        if setting:
            parts.append(setting)

        # 5. Lighting from continuity
        lighting = continuity.get("lighting_recipe")
        if lighting:
            lighting_text = self._describe_lighting(lighting)
            parts.append(lighting_text)

        # 6. Color palette from continuity
        palette = continuity.get("palette_anchors", [])
        if palette:
            palette_text = self._describe_palette(palette)
            parts.append(palette_text)

        # 7. Style clause
        style = continuity.get("style_clause")
        if style:
            parts.append(f"Style: {style}")

        # 8. Do list as guidance
        do_list = continuity.get("do_list", [])
        if do_list:
            # Pick relevant items (first 2-3)
            guidance = ". ".join(do_list[:3])
            parts.append(guidance)

        # 9. Exclusions woven into prompt (avoid section)
        exclusions = self._build_exclusions(continuity, brief)
        if exclusions:
            parts.append(exclusions)

        return "\n\n".join(parts)

    def _build_exclusions(self, continuity: dict, brief: dict) -> str:
        """Build exclusions section woven into the main prompt."""
        exclusion_parts = []

        # Don't list from continuity
        dont_list = continuity.get("dont_list", [])
        if dont_list:
            exclusion_parts.extend(dont_list)

        # Avoid vibe from brief
        avoid_vibe = brief.get("avoid_vibe", [])
        if avoid_vibe:
            avoid_vibe_items = [f"no {v} aesthetic" for v in avoid_vibe if v]
            exclusion_parts.extend(avoid_vibe_items)

        # Must avoid from brief
        must_avoid = brief.get("must_avoid", [])
        if must_avoid:
            exclusion_parts.extend([f"avoid {item}" for item in must_avoid])

        # Common video quality exclusions
        quality_exclusions = [
            "no distorted faces",
            "no extra limbs",
            "avoid blurry footage",
            "no visual artifacts or glitches",
        ]
        exclusion_parts.extend(quality_exclusions)

        if exclusion_parts:
            return "Important: " + ". ".join(exclusion_parts) + "."
        return ""

    def _get_sora_params(self, shot: dict, brief: dict) -> dict:
        """Get Sora 2 API parameters for the shot."""
        duration = shot.get("end_sec", 0) - shot.get("start_sec", 0)
        aspect_ratio = brief.get("aspect_ratio", "16:9")

        return {
            "resolution": "1080p",
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "fps": 24,
        }

    def _extract_dialogue(self, shot: dict, brief: dict) -> Optional[str]:
        """Extract dialogue block if present."""
        # Check if shot has audio cue that suggests dialogue
        audio_cue = shot.get("audio_cue", "")

        # Check brief for script
        script = brief.get("script_or_vo", "")

        # For now, return None - dialogue extraction would need more context
        # In a full implementation, this would parse script timestamps
        return None

    def _describe_camera_move(self, move: str, duration: float) -> str:
        """Describe camera movement in natural language."""
        move_descriptions = {
            "pan": f"Camera pans smoothly over {duration:.1f} seconds",
            "tilt": f"Camera tilts slowly over {duration:.1f} seconds",
            "orbit": f"Camera orbits around the subject over {duration:.1f} seconds",
            "push_in": f"Camera slowly pushes in toward the subject over {duration:.1f} seconds",
            "pull_out": f"Camera slowly pulls out from the subject over {duration:.1f} seconds",
            "crane": f"Camera executes a crane movement over {duration:.1f} seconds",
            "none": "Static camera, locked off",
        }
        return move_descriptions.get(move, f"Camera moves ({move}) over {duration:.1f} seconds")

    def _describe_actions(self, beats: list[str], continuity: dict) -> str:
        """Describe subject actions incorporating continuity anchors."""
        # Get character anchor if available
        character = None
        for anchor in continuity.get("anchors", []):
            if anchor.get("type") == "character":
                character = anchor.get("description")
                break

        if character:
            intro = f"Subject ({character}): "
        else:
            intro = "Action sequence: "

        action_list = ". ".join(beats)
        return intro + action_list

    def _describe_lighting(self, lighting: dict) -> str:
        """Describe lighting in natural language."""
        parts = []

        key = lighting.get("key_light")
        if key:
            parts.append(f"Key light: {key}")

        fill = lighting.get("fill_light")
        if fill:
            parts.append(f"Fill: {fill}")

        rim = lighting.get("rim_light")
        if rim:
            parts.append(f"Rim/accent: {rim}")

        softness = lighting.get("softness")
        time_of_day = lighting.get("time_of_day")
        if softness or time_of_day:
            parts.append(f"{softness or ''} {time_of_day or ''} lighting".strip())

        return " ".join(parts) if parts else ""

    def _describe_palette(self, palette: list[dict]) -> str:
        """Describe color palette."""
        if not palette:
            return ""

        colors = [f"{p.get('name', '')} ({p.get('hex', '')})" for p in palette[:5]]
        return f"Color palette: {', '.join(colors)}"


def get_compiler(model: str) -> BasePromptCompiler:
    """
    Factory function to get the appropriate compiler for a model.

    Args:
        model: Model identifier (e.g., "sora_2", "runway_gen4")

    Returns:
        BasePromptCompiler instance
    """
    compilers = {
        "sora_2": Sora2Compiler,
        # Future compilers:
        # "runway_gen4": RunwayGen4Compiler,
        # "kling": KlingCompiler,
        # "veo": VeoCompiler,
    }

    compiler_class = compilers.get(model, Sora2Compiler)
    return compiler_class()


def compile_all_shots(
    shots: list[dict],
    continuity: dict,
    brief: dict,
    target_model: str = "sora_2",
) -> dict:
    """
    Compile all shots into a prompt pack.

    Args:
        shots: List of shot data from shot plan
        continuity: Continuity pack data
        brief: Brief intake data
        target_model: Target video generation model

    Returns:
        Dict with target_model and list of compiled prompts
    """
    compiler = get_compiler(target_model)

    prompts = []
    for shot in shots:
        compiled = compiler.compile_shot(shot, continuity, brief)
        prompts.append(compiled)

    return {
        "target_model": target_model,
        "prompts": prompts,
    }
