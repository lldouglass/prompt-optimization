"""
Planner Agent - Selects appropriate skills for user requests.

The planner analyzes a user request and the catalog of available
skills, then outputs a plan specifying which skill(s) to use.
"""

import json
import re
from dataclasses import dataclass, field
from typing import Any

from llm import LLMClient
from prompts import SkillRegistry

PLANNER_SYSTEM_PROMPT = """You are a planning assistant that routes user requests to the most appropriate skill.

Given a user request and a catalog of available skills, analyze the request and select the best skill(s) to handle it.

Output your response as a JSON object with this structure:
{
  "reasoning": "Brief explanation of why you chose this skill",
  "steps": [
    {
      "skill": "skill_name",
      "input_mapping": {"input": "user_request"},
      "notes": "Any specific instructions for this step"
    }
  ]
}

Rules:
1. Select the most specific skill that matches the request
2. Use "general_assistant" only as a fallback when no other skill fits
3. For complex requests, you may select multiple skills to execute in sequence
4. Keep input_mapping simple - usually just passing the user input
5. Be concise in your reasoning
"""


@dataclass
class PlanStep:
    """A single step in an execution plan."""

    skill: str
    input_mapping: dict[str, str] = field(default_factory=dict)
    notes: str = ""


@dataclass
class Plan:
    """An execution plan produced by the planner."""

    reasoning: str
    steps: list[PlanStep]
    raw_response: str = ""

    @property
    def is_valid(self) -> bool:
        """Check if the plan has at least one step."""
        return len(self.steps) > 0

    @property
    def skill_names(self) -> list[str]:
        """Get list of skill names in the plan."""
        return [step.skill for step in self.steps]


class Planner:
    """
    Planner agent that selects skills for user requests.

    Uses an LLM to analyze user requests and match them
    to appropriate skills from the registry.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        registry: SkillRegistry,
        model: str = "gpt-4.1",
    ):
        """
        Initialize the planner.

        Args:
            llm_client: LLM client for generating plans.
            registry: Skill registry to select from.
            model: Model to use for planning.
        """
        self.llm = llm_client
        self.registry = registry
        self.model = model

    def plan(self, user_request: str) -> Plan:
        """
        Create an execution plan for a user request.

        Args:
            user_request: The user's request text.

        Returns:
            A Plan object with selected skills and reasoning.
        """
        catalog = self.registry.get_catalog()

        messages = [
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"SKILL CATALOG:\n{catalog}\n\nUSER REQUEST:\n{user_request}",
            },
        ]

        response = self.llm.complete_chat(
            messages,
            model=self.model,
            max_tokens=512,
            temperature=0.3,
        )

        return self._parse_plan(response.content)

    def _parse_plan(self, response: str) -> Plan:
        """Parse the LLM response into a Plan object."""
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if not json_match:
                return self._fallback_plan(response)

            data = json.loads(json_match.group())

            steps = []
            for step_data in data.get("steps", []):
                steps.append(PlanStep(
                    skill=step_data.get("skill", "general_assistant"),
                    input_mapping=step_data.get("input_mapping", {"input": "user_request"}),
                    notes=step_data.get("notes", ""),
                ))

            return Plan(
                reasoning=data.get("reasoning", ""),
                steps=steps,
                raw_response=response,
            )

        except (json.JSONDecodeError, KeyError, TypeError):
            return self._fallback_plan(response)

    def _fallback_plan(self, response: str) -> Plan:
        """Create a fallback plan when parsing fails."""
        return Plan(
            reasoning="Failed to parse planner response, using fallback",
            steps=[PlanStep(skill="general_assistant", input_mapping={"input": "user_request"})],
            raw_response=response,
        )

    def validate_plan(self, plan: Plan) -> tuple[bool, list[str]]:
        """
        Validate that all skills in a plan exist.

        Args:
            plan: The plan to validate.

        Returns:
            Tuple of (is_valid, list of error messages).
        """
        errors = []

        for step in plan.steps:
            if step.skill not in self.registry:
                errors.append(f"Unknown skill: {step.skill}")

        return len(errors) == 0, errors
