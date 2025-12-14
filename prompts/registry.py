"""
Skill Registry - Loads and manages prompt skills from YAML files.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class Skill:
    """Represents a single prompt skill loaded from YAML."""

    name: str
    description: str
    tags: list[str]
    model: str
    max_tokens: int
    temperature: float
    prompt_template: str

    # Optional metadata
    extra: dict[str, Any] = field(default_factory=dict)

    def render(self, **kwargs: Any) -> str:
        """
        Render the prompt template with provided variables.

        Supports simple {{variable}} substitution and basic
        {{#if variable}}...{{/if}} conditionals.
        """
        result = self.prompt_template

        # Handle conditionals first: {{#if var}}content{{/if}}
        conditional_pattern = r'\{\{#if\s+(\w+)\}\}(.*?)\{\{/if\}\}'

        def replace_conditional(match: re.Match) -> str:
            var_name = match.group(1)
            content = match.group(2)
            if kwargs.get(var_name):
                # Recursively render the content inside the conditional
                return content
            return ""

        result = re.sub(conditional_pattern, replace_conditional, result, flags=re.DOTALL)

        # Handle simple variable substitution: {{variable}}
        for key, value in kwargs.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))

        # Clean up any remaining unsubstituted variables
        result = re.sub(r'\{\{[^}]+\}\}', '', result)

        return result.strip()


class SkillRegistry:
    """
    Registry for loading and accessing prompt skills.

    Skills are loaded from YAML files in a specified directory.
    """

    def __init__(self, skills_dir: str | Path | None = None):
        """
        Initialize the registry.

        Args:
            skills_dir: Directory containing skill YAML files.
                       Defaults to prompts/skills/ relative to this file.
        """
        if skills_dir is None:
            skills_dir = Path(__file__).parent / "skills"
        self.skills_dir = Path(skills_dir)
        self._skills: dict[str, Skill] = {}
        self._loaded = False

    def load(self) -> None:
        """Load all skills from the skills directory."""
        if not self.skills_dir.exists():
            raise FileNotFoundError(f"Skills directory not found: {self.skills_dir}")

        self._skills.clear()

        for yaml_file in self.skills_dir.glob("*.yaml"):
            skill = self._load_skill(yaml_file)
            self._skills[skill.name] = skill

        self._loaded = True

    def _load_skill(self, path: Path) -> Skill:
        """Load a single skill from a YAML file."""
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # Extract known fields
        known_fields = {
            "name", "description", "tags", "model",
            "max_tokens", "temperature", "prompt_template"
        }
        extra = {k: v for k, v in data.items() if k not in known_fields}

        return Skill(
            name=data["name"],
            description=data["description"],
            tags=data.get("tags", []),
            model=data.get("model", "gpt-4.1"),
            max_tokens=data.get("max_tokens", 1024),
            temperature=data.get("temperature", 0.7),
            prompt_template=data["prompt_template"],
            extra=extra,
        )

    def _ensure_loaded(self) -> None:
        """Ensure skills have been loaded."""
        if not self._loaded:
            self.load()

    def get(self, name: str) -> Skill | None:
        """Get a skill by name."""
        self._ensure_loaded()
        return self._skills.get(name)

    def get_all(self) -> list[Skill]:
        """Get all loaded skills."""
        self._ensure_loaded()
        return list(self._skills.values())

    def get_by_tag(self, tag: str) -> list[Skill]:
        """Get all skills with a specific tag."""
        self._ensure_loaded()
        return [s for s in self._skills.values() if tag in s.tags]

    def get_catalog(self) -> str:
        """
        Get a formatted catalog of all skills for the planner.

        Returns a string listing all skills with their names,
        descriptions, and tags.
        """
        self._ensure_loaded()

        lines = ["Available Skills:", "=" * 40]

        for skill in sorted(self._skills.values(), key=lambda s: s.name):
            lines.append(f"\n[{skill.name}]")
            lines.append(f"  Description: {skill.description}")
            lines.append(f"  Tags: {', '.join(skill.tags)}")
            lines.append(f"  Model: {skill.model}")

        return "\n".join(lines)

    def __len__(self) -> int:
        """Return the number of loaded skills."""
        self._ensure_loaded()
        return len(self._skills)

    def __contains__(self, name: str) -> bool:
        """Check if a skill exists by name."""
        self._ensure_loaded()
        return name in self._skills
