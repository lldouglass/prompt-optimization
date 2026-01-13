"""Tests for the video workflow prompt compiler."""

import pytest
import sys
from pathlib import Path

# Add backend path for imports
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from app.services.video_workflow.compiler import (
    Sora2Compiler,
    compile_all_shots,
    get_compiler,
)
from app.services.video_workflow.mocks import (
    MOCK_BRIEF,
    MOCK_CONTINUITY_PACK,
    MOCK_SHOT_PLAN,
)


class TestSora2Compiler:
    """Tests for the Sora 2 prompt compiler."""

    def setup_method(self):
        """Set up test fixtures."""
        self.compiler = Sora2Compiler()

    def test_compile_single_shot(self):
        """Test compiling a single shot to prompt."""
        shot = MOCK_SHOT_PLAN["shots"][0]

        result = self.compiler.compile_shot(shot, MOCK_CONTINUITY_PACK, MOCK_BRIEF)

        assert "shot_id" in result
        assert "prompt_text" in result
        assert "sora_params" in result
        assert result["sora_params"]["aspect_ratio"] == MOCK_BRIEF["aspect_ratio"]

    def test_prompt_text_includes_shot_type(self):
        """Prompt text should include the shot type."""
        shot = {
            "id": "test-shot",
            "shot_number": 1,
            "shot_type": "wide",
            "camera_move": "none",
            "framing_notes": "test framing",
            "subject_action_beats": ["action 1"],
            "start_sec": 0,
            "end_sec": 5,
            "purpose": "test purpose",
        }

        result = self.compiler.compile_shot(shot, MOCK_CONTINUITY_PACK, MOCK_BRIEF)

        assert "wide" in result["prompt_text"].lower()

    def test_prompt_text_includes_camera_move(self):
        """Prompt text should include camera movement."""
        shot = {
            "id": "test-shot",
            "shot_number": 1,
            "shot_type": "medium",
            "camera_move": "push_in",
            "framing_notes": "test framing",
            "subject_action_beats": ["action 1"],
            "start_sec": 0,
            "end_sec": 5,
            "purpose": "test purpose",
        }

        result = self.compiler.compile_shot(shot, MOCK_CONTINUITY_PACK, MOCK_BRIEF)

        # The camera move description should mention "push"
        assert "push" in result["prompt_text"].lower()

    def test_prompt_includes_style_clause(self):
        """Prompt should include the style clause from continuity pack."""
        shot = MOCK_SHOT_PLAN["shots"][0]

        result = self.compiler.compile_shot(shot, MOCK_CONTINUITY_PACK, MOCK_BRIEF)

        style_clause = MOCK_CONTINUITY_PACK.get("style_clause", "")
        if style_clause:
            # Style clause should be present
            assert "style" in result["prompt_text"].lower()

    def test_sora_params_correct_format(self):
        """Sora params should have correct format and values."""
        shot = {
            "id": "test-shot",
            "shot_number": 1,
            "shot_type": "wide",
            "camera_move": "none",
            "framing_notes": "test",
            "subject_action_beats": [],
            "start_sec": 0,
            "end_sec": 5,
            "purpose": "test",
        }
        brief = {**MOCK_BRIEF, "aspect_ratio": "9:16"}

        result = self.compiler.compile_shot(shot, MOCK_CONTINUITY_PACK, brief)

        params = result["sora_params"]
        assert params["aspect_ratio"] == "9:16"
        assert params["duration"] == 5  # end_sec - start_sec
        assert params["resolution"] in ["1080p", "720p"]
        assert params["fps"] in [24, 30, 60]

    def test_duration_calculation(self):
        """Duration should be calculated from shot timing."""
        shot = {
            "id": "test-shot",
            "shot_number": 1,
            "shot_type": "wide",
            "camera_move": "none",
            "framing_notes": "test",
            "subject_action_beats": [],
            "start_sec": 2.5,
            "end_sec": 7.5,
            "purpose": "test",
        }

        result = self.compiler.compile_shot(shot, MOCK_CONTINUITY_PACK, MOCK_BRIEF)

        assert result["sora_params"]["duration"] == 5  # 7.5 - 2.5 = 5

    def test_get_model_name(self):
        """Compiler should return correct model name."""
        assert self.compiler.get_model_name() == "sora_2"


class TestBuildPromptText:
    """Tests for prompt text building."""

    def setup_method(self):
        """Set up test fixtures."""
        self.compiler = Sora2Compiler()

    def test_prompt_not_empty(self):
        """Built prompt should not be empty."""
        shot = MOCK_SHOT_PLAN["shots"][0]

        result = self.compiler.compile_shot(shot, MOCK_CONTINUITY_PACK, MOCK_BRIEF)

        assert len(result["prompt_text"]) > 0

    def test_prompt_includes_action_beats(self):
        """Prompt should incorporate action beats."""
        shot = {
            "id": "test-shot",
            "shot_number": 1,
            "shot_type": "medium",
            "camera_move": "none",
            "framing_notes": "test",
            "subject_action_beats": ["character walks forward", "character smiles"],
            "start_sec": 0,
            "end_sec": 5,
            "purpose": "show emotion",
        }

        result = self.compiler.compile_shot(shot, MOCK_CONTINUITY_PACK, MOCK_BRIEF)

        # Action beats should be reflected in prompt
        assert "walk" in result["prompt_text"].lower() or "smil" in result["prompt_text"].lower()

    def test_prompt_includes_framing_notes(self):
        """Prompt should include framing notes."""
        shot = {
            "id": "test-shot",
            "shot_number": 1,
            "shot_type": "close-up",
            "camera_move": "none",
            "framing_notes": "focus on hands holding coffee cup",
            "subject_action_beats": [],
            "start_sec": 0,
            "end_sec": 3,
            "purpose": "detail shot",
        }

        result = self.compiler.compile_shot(shot, MOCK_CONTINUITY_PACK, MOCK_BRIEF)

        assert "hands" in result["prompt_text"].lower() or "coffee" in result["prompt_text"].lower()


class TestBuildNegativePrompt:
    """Tests for negative prompt building."""

    def setup_method(self):
        """Set up test fixtures."""
        self.compiler = Sora2Compiler()

    def test_negative_prompt_from_dont_list(self):
        """Negative prompt should incorporate don't list items."""
        continuity = {
            **MOCK_CONTINUITY_PACK,
            "dont_list": ["harsh shadows", "cool tones", "fast motion"],
        }
        shot = MOCK_SHOT_PLAN["shots"][0]

        result = self.compiler.compile_shot(shot, continuity, MOCK_BRIEF)

        # Should include some don't list items
        assert len(result["negative_prompt_text"]) > 0

    def test_empty_dont_list_still_works(self):
        """Should handle empty don't list gracefully."""
        continuity = {
            **MOCK_CONTINUITY_PACK,
            "dont_list": [],
        }
        shot = MOCK_SHOT_PLAN["shots"][0]

        result = self.compiler.compile_shot(shot, continuity, MOCK_BRIEF)

        # Should not raise, will have common negatives
        assert isinstance(result["negative_prompt_text"], str)


class TestCompileAllShots:
    """Tests for the full compilation pipeline."""

    def test_compile_all_returns_dict(self):
        """Compile all shots should return a dict with prompts list."""
        result = compile_all_shots(
            MOCK_SHOT_PLAN["shots"],
            MOCK_CONTINUITY_PACK,
            MOCK_BRIEF,
            "sora_2",
        )

        assert isinstance(result, dict)
        assert "prompts" in result
        assert "target_model" in result
        assert len(result["prompts"]) == len(MOCK_SHOT_PLAN["shots"])

    def test_each_prompt_has_required_fields(self):
        """Each compiled prompt should have all required fields."""
        result = compile_all_shots(
            MOCK_SHOT_PLAN["shots"],
            MOCK_CONTINUITY_PACK,
            MOCK_BRIEF,
            "sora_2",
        )

        for prompt in result["prompts"]:
            assert "shot_id" in prompt
            assert "prompt_text" in prompt
            assert "sora_params" in prompt
            assert "negative_prompt_text" in prompt

    def test_prompts_maintain_shot_order(self):
        """Compiled prompts should maintain shot order."""
        result = compile_all_shots(
            MOCK_SHOT_PLAN["shots"],
            MOCK_CONTINUITY_PACK,
            MOCK_BRIEF,
            "sora_2",
        )

        for i, (shot, prompt) in enumerate(zip(MOCK_SHOT_PLAN["shots"], result["prompts"])):
            assert prompt["shot_id"] == shot["id"]


class TestGetCompiler:
    """Tests for the compiler factory function."""

    def test_get_sora2_compiler(self):
        """Should return Sora2Compiler for sora_2."""
        compiler = get_compiler("sora_2")
        assert isinstance(compiler, Sora2Compiler)

    def test_unknown_model_returns_default(self):
        """Unknown model should return default (Sora2) compiler."""
        compiler = get_compiler("unknown_model")
        # Should return Sora2Compiler as default
        assert isinstance(compiler, Sora2Compiler)
