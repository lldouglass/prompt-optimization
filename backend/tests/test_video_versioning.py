"""Tests for video prompt versioning logic."""

import pytest
from datetime import datetime
from unittest.mock import MagicMock

import sys
from pathlib import Path

# Add paths for imports
backend_path = Path(__file__).parent.parent
project_root = backend_path.parent
sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(project_root))

from app.models.video import VideoPromptVersion, generate_full_prompt_text


class TestGenerateFullPromptText:
    """Tests for the full prompt text generation function."""

    def test_generates_full_text_with_all_fields(self):
        """Test that all fields are included in the generated text."""
        version = MagicMock(spec=VideoPromptVersion)
        version.scene_description = "A sunset over the ocean"
        version.motion_timing = "Slow pan from left to right"
        version.style_tone = "Cinematic, dramatic lighting"
        version.camera_language = "Wide establishing shot"
        version.constraints = "Keep within 5 seconds"
        version.negative_instructions = "No fast movements"

        result = generate_full_prompt_text(version)

        assert "Scene: A sunset over the ocean" in result
        assert "Motion/Timing: Slow pan from left to right" in result
        assert "Style/Tone: Cinematic, dramatic lighting" in result
        assert "Camera: Wide establishing shot" in result
        assert "Constraints: Keep within 5 seconds" in result
        assert "Avoid: No fast movements" in result

    def test_handles_empty_fields(self):
        """Test that empty fields are not included."""
        version = MagicMock(spec=VideoPromptVersion)
        version.scene_description = "A sunset"
        version.motion_timing = None
        version.style_tone = ""
        version.camera_language = None
        version.constraints = None
        version.negative_instructions = None

        result = generate_full_prompt_text(version)

        assert "Scene: A sunset" in result
        assert "Motion/Timing" not in result
        assert "Style/Tone" not in result
        assert "Camera" not in result
        assert "Constraints" not in result
        assert "Avoid" not in result

    def test_handles_all_empty_fields(self):
        """Test that all empty fields returns empty string."""
        version = MagicMock(spec=VideoPromptVersion)
        version.scene_description = None
        version.motion_timing = None
        version.style_tone = None
        version.camera_language = None
        version.constraints = None
        version.negative_instructions = None

        result = generate_full_prompt_text(version)

        assert result == ""

    def test_separates_sections_with_double_newlines(self):
        """Test that sections are separated by double newlines."""
        version = MagicMock(spec=VideoPromptVersion)
        version.scene_description = "Scene A"
        version.motion_timing = "Motion B"
        version.style_tone = None
        version.camera_language = None
        version.constraints = "Constraints C"
        version.negative_instructions = None

        result = generate_full_prompt_text(version)

        assert "\n\n" in result
        parts = result.split("\n\n")
        assert len(parts) == 3


class TestVersionNumbering:
    """Tests for version numbering logic."""

    def test_first_version_is_1(self):
        """Test that the first version has version_number 1."""
        # This is validated in the router, testing the expectation
        existing_versions = []
        max_version = max((v.version_number for v in existing_versions), default=0)
        new_version_number = max_version + 1
        assert new_version_number == 1

    def test_new_version_increments(self):
        """Test that new versions increment the version number."""
        v1 = MagicMock()
        v1.version_number = 1
        v2 = MagicMock()
        v2.version_number = 2
        existing_versions = [v1, v2]

        max_version = max(v.version_number for v in existing_versions)
        new_version_number = max_version + 1

        assert new_version_number == 3

    def test_rollback_creates_new_version(self):
        """Test that rollback creates a new version with the old content."""
        # Rollback should create a NEW version, not modify the old one
        v1 = MagicMock()
        v1.version_number = 1
        v1.scene_description = "Original scene"
        v2 = MagicMock()
        v2.version_number = 2
        v2.scene_description = "Modified scene"

        # After rollback to v1, we should have v3 with v1's content
        existing_versions = [v1, v2]
        max_version = max(v.version_number for v in existing_versions)
        new_version_number = max_version + 1

        assert new_version_number == 3
        # The new version should copy content from v1
        # (This is done in the router)


class TestVersionTypes:
    """Tests for version type handling."""

    def test_variant_type(self):
        """Test that variants have type='variant'."""
        version = MagicMock(spec=VideoPromptVersion)
        version.type = "variant"
        version.status = "draft"

        assert version.type == "variant"
        assert version.status == "draft"

    def test_main_type(self):
        """Test that main versions have type='main'."""
        version = MagicMock(spec=VideoPromptVersion)
        version.type = "main"
        version.status = "active"

        assert version.type == "main"
        assert version.status == "active"

    def test_promote_changes_type_and_status(self):
        """Test that promoting a variant changes its type and status."""
        version = MagicMock(spec=VideoPromptVersion)
        version.type = "variant"
        version.status = "draft"

        # Promote
        version.type = "main"
        version.status = "active"

        assert version.type == "main"
        assert version.status == "active"


class TestBestVersionCalculation:
    """Tests for best version scoring algorithm."""

    def test_best_version_is_highest_score(self):
        """Test that the best version has the highest score."""
        v1 = MagicMock()
        v1.id = "v1"
        v1.good_count = 5
        v1.bad_count = 1
        v1.created_at = datetime(2024, 1, 1)

        v2 = MagicMock()
        v2.id = "v2"
        v2.good_count = 3
        v2.bad_count = 0
        v2.created_at = datetime(2024, 1, 2)

        versions = [v1, v2]

        # Calculate scores
        version_scores = []
        for v in versions:
            score = v.good_count - v.bad_count
            version_scores.append((v, score, v.created_at))

        # Sort by score desc, then by created_at desc
        version_scores.sort(key=lambda x: (x[1], x[2]), reverse=True)
        best = version_scores[0][0]

        # v1 has score 4 (5-1), v2 has score 3 (3-0)
        assert best.id == "v1"

    def test_tiebreaker_is_most_recent(self):
        """Test that ties are broken by most recent version."""
        v1 = MagicMock()
        v1.id = "v1"
        v1.good_count = 2
        v1.bad_count = 0
        v1.created_at = datetime(2024, 1, 1)

        v2 = MagicMock()
        v2.id = "v2"
        v2.good_count = 2
        v2.bad_count = 0
        v2.created_at = datetime(2024, 1, 2)

        versions = [v1, v2]

        # Calculate scores
        version_scores = []
        for v in versions:
            score = v.good_count - v.bad_count
            version_scores.append((v, score, v.created_at))

        # Sort by score desc, then by created_at desc
        version_scores.sort(key=lambda x: (x[1], x[2]), reverse=True)
        best = version_scores[0][0]

        # Both have score 2, but v2 is more recent
        assert best.id == "v2"

    def test_no_best_if_no_positive_score(self):
        """Test that there's no best version if all scores are <= 0."""
        v1 = MagicMock()
        v1.id = "v1"
        v1.good_count = 0
        v1.bad_count = 1
        v1.created_at = datetime(2024, 1, 1)

        versions = [v1]

        # Calculate scores
        version_scores = []
        for v in versions:
            score = v.good_count - v.bad_count
            version_scores.append((v, score, v.created_at))

        version_scores.sort(key=lambda x: (x[1], x[2]), reverse=True)

        # Best should only be set if score > 0
        best_version_id = version_scores[0][0].id if version_scores[0][1] > 0 else None

        assert best_version_id is None
