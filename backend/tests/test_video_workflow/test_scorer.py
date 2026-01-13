"""Tests for the video workflow QA scorer."""

import pytest
import sys
from pathlib import Path

# Add backend path for imports
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from app.services.video_workflow.scorer import (
    calculate_ambiguity_risk,
    calculate_motion_complexity_risk,
    calculate_continuity_completeness,
    calculate_audio_readiness,
    calculate_overall_score,
    generate_warnings,
    generate_fixes,
    score_workflow,
)
from app.services.video_workflow.mocks import (
    MOCK_BRIEF,
    MOCK_CONTINUITY_PACK,
    MOCK_SHOT_PLAN,
    MOCK_PROMPT_PACK,
)


class TestAmbiguityRisk:
    """Tests for ambiguity risk calculation."""

    def test_low_ambiguity_with_good_prompts(self):
        """Well-written prompts should have low ambiguity risk."""
        prompts = MOCK_PROMPT_PACK["prompts"]
        score = calculate_ambiguity_risk(prompts)
        # Good prompts should have risk below 50
        assert 0 <= score <= 50

    def test_high_ambiguity_with_short_prompts(self):
        """Short prompts should have higher ambiguity risk."""
        prompts = [
            {"prompt_text": "A scene."},
            {"prompt_text": "Nice shot."},
        ]
        score = calculate_ambiguity_risk(prompts)
        # Short prompts add risk
        assert score >= 20

    def test_vague_adjectives_increase_risk(self):
        """Vague adjectives like 'nice', 'good' should increase risk."""
        prompts = [
            {"prompt_text": "A nice scene with good lighting and interesting elements that is very beautiful."},
        ]
        score = calculate_ambiguity_risk(prompts)
        # Multiple vague adjectives should add risk
        assert score >= 10

    def test_empty_prompts_max_risk(self):
        """Empty prompts should have maximum risk."""
        prompts = [{"prompt_text": ""}]
        score = calculate_ambiguity_risk(prompts)
        assert score >= 20

    def test_no_prompts_max_risk(self):
        """No prompts should return max risk."""
        score = calculate_ambiguity_risk([])
        assert score == 100


class TestMotionComplexityRisk:
    """Tests for motion complexity risk calculation."""

    def test_simple_shots_low_risk(self):
        """Simple shots should have low motion risk."""
        shots = MOCK_SHOT_PLAN["shots"]
        score = calculate_motion_complexity_risk(shots)
        # Well-planned shots should have reasonable risk
        assert 0 <= score <= 50

    def test_compound_camera_moves_increase_risk(self):
        """Compound camera moves should increase risk."""
        shots = [
            {
                "camera_move": "dolly-in and pan left",
                "framing_notes": "",
                "subject_action_beats": ["beat 1"],
                "start_sec": 0,
                "end_sec": 5,
            },
        ]
        score = calculate_motion_complexity_risk(shots)
        # Compound moves add risk
        assert score >= 20

    def test_many_action_beats_increase_risk(self):
        """Many action beats in one shot should increase risk."""
        shots = [
            {
                "camera_move": "none",
                "framing_notes": "",
                "subject_action_beats": ["beat 1", "beat 2", "beat 3", "beat 4", "beat 5"],
                "start_sec": 0,
                "end_sec": 5,
            },
        ]
        score = calculate_motion_complexity_risk(shots)
        # More than 4 beats adds risk
        assert score >= 10

    def test_short_duration_with_movement_increases_risk(self):
        """Short duration shots with movement are risky."""
        shots = [
            {
                "camera_move": "dolly-in",
                "framing_notes": "",
                "subject_action_beats": [],
                "start_sec": 0,
                "end_sec": 1.5,  # Less than 2 seconds
            },
        ]
        score = calculate_motion_complexity_risk(shots)
        # Short duration with movement adds risk
        assert score >= 15

    def test_no_shots_zero_risk(self):
        """No shots should return zero risk."""
        score = calculate_motion_complexity_risk([])
        assert score == 0


class TestContinuityCompleteness:
    """Tests for continuity completeness calculation."""

    def test_complete_continuity_high_score(self):
        """Complete continuity pack should score high."""
        score = calculate_continuity_completeness(MOCK_CONTINUITY_PACK)
        # Complete pack should score 60+
        assert score >= 60

    def test_empty_continuity_low_score(self):
        """Empty continuity pack should score low."""
        empty_pack = {
            "anchors": [],
            "lighting_recipe": None,
            "palette_anchors": [],
            "do_list": [],
            "dont_list": [],
            "style_clause": "",
        }
        score = calculate_continuity_completeness(empty_pack)
        assert score == 0

    def test_partial_continuity_moderate_score(self):
        """Partial continuity pack should score moderately."""
        partial_pack = {
            "anchors": [{"type": "character", "description": "test"}],
            "lighting_recipe": {"key_light": "natural"},
            "palette_anchors": [],
            "do_list": [],
            "dont_list": [],
            "style_clause": "",
        }
        score = calculate_continuity_completeness(partial_pack)
        # Has anchors (20) and lighting (20) = 40
        assert 35 <= score <= 45

    def test_none_continuity_zero_score(self):
        """None continuity should return zero."""
        score = calculate_continuity_completeness(None)
        assert score == 0


class TestAudioReadiness:
    """Tests for audio readiness calculation."""

    def test_no_dialogue_full_readiness(self):
        """No dialogue projects should have high audio readiness."""
        brief = {**MOCK_BRIEF, "script_or_vo": None}
        shots = [{"audio_cue": None} for _ in range(4)]
        score = calculate_audio_readiness(shots, brief)
        # Should still be relatively high
        assert score >= 60

    def test_dialogue_without_audio_cues_lower_score(self):
        """Dialogue projects without audio cues should score lower."""
        brief = {**MOCK_BRIEF, "script_or_vo": "Hello world"}
        shots = [{"audio_cue": None}, {"audio_cue": None}]  # Missing audio cues
        score = calculate_audio_readiness(shots, brief)
        # Missing cues and blocks reduce score
        assert score < 100

    def test_no_shots_full_score(self):
        """No shots should return full score."""
        score = calculate_audio_readiness([])
        assert score == 100


class TestOverallScore:
    """Tests for overall score calculation."""

    def test_overall_score_weighted_average(self):
        """Overall score should be a weighted combination of all scores."""
        overall = calculate_overall_score(
            ambiguity_risk=10,
            motion_complexity_risk=10,
            continuity_completeness=100,
            audio_readiness=100,
        )
        # Should be high with low risks and high completeness
        assert 70 <= overall <= 100

    def test_overall_score_bounds(self):
        """Overall score should always be between 0 and 100."""
        # High risk scenario
        high_risk = calculate_overall_score(
            ambiguity_risk=100,
            motion_complexity_risk=100,
            continuity_completeness=0,
            audio_readiness=0,
        )
        assert 0 <= high_risk <= 100

        # Low risk scenario
        low_risk = calculate_overall_score(
            ambiguity_risk=0,
            motion_complexity_risk=0,
            continuity_completeness=100,
            audio_readiness=100,
        )
        assert 0 <= low_risk <= 100


class TestWarningsAndFixes:
    """Tests for warning and fix generation."""

    def test_generate_warnings_returns_list(self):
        """Generate warnings should return a list."""
        shots = MOCK_SHOT_PLAN["shots"]
        prompts = MOCK_PROMPT_PACK["prompts"]
        warnings = generate_warnings(shots, prompts, MOCK_CONTINUITY_PACK, MOCK_BRIEF)
        assert isinstance(warnings, list)

    def test_generate_fixes_returns_list_of_dicts(self):
        """Generate fixes should return a list of dicts with issue/fix keys."""
        shots = MOCK_SHOT_PLAN["shots"]
        prompts = MOCK_PROMPT_PACK["prompts"]
        fixes = generate_fixes(shots, prompts, MOCK_CONTINUITY_PACK)
        assert isinstance(fixes, list)
        for fix in fixes:
            assert "issue" in fix
            assert "fix" in fix

    def test_missing_continuity_generates_warning(self):
        """Missing continuity elements should generate warnings."""
        shots = MOCK_SHOT_PLAN["shots"]
        prompts = MOCK_PROMPT_PACK["prompts"]
        continuity = {
            "anchors": [],
            "lighting_recipe": None,
            "palette_anchors": [],
            "do_list": [],
            "dont_list": [],
            "style_clause": "",
        }
        warnings = generate_warnings(shots, prompts, continuity, MOCK_BRIEF)
        # Should have warnings about missing continuity elements
        assert len(warnings) > 0


class TestScoreWorkflow:
    """Tests for the complete workflow scoring function."""

    def test_score_workflow_returns_all_fields(self):
        """score_workflow should return all required fields."""
        result = score_workflow(
            brief=MOCK_BRIEF,
            continuity=MOCK_CONTINUITY_PACK,
            shots=MOCK_SHOT_PLAN["shots"],
            prompts=MOCK_PROMPT_PACK["prompts"],
        )

        assert "ambiguity_risk" in result
        assert "motion_complexity_risk" in result
        assert "continuity_completeness" in result
        assert "audio_readiness" in result
        assert "overall_score" in result
        assert "warnings" in result
        assert "fixes" in result
        assert "recommended_questions" in result

    def test_score_workflow_all_scores_in_range(self):
        """All scores should be in 0-100 range."""
        result = score_workflow(
            brief=MOCK_BRIEF,
            continuity=MOCK_CONTINUITY_PACK,
            shots=MOCK_SHOT_PLAN["shots"],
            prompts=MOCK_PROMPT_PACK["prompts"],
        )

        assert 0 <= result["ambiguity_risk"] <= 100
        assert 0 <= result["motion_complexity_risk"] <= 100
        assert 0 <= result["continuity_completeness"] <= 100
        assert 0 <= result["audio_readiness"] <= 100
        assert 0 <= result["overall_score"] <= 100
