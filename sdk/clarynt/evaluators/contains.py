from typing import Any
from .base import BaseEvaluator


class Contains(BaseEvaluator):
    """Check if output contains expected strings."""

    def __init__(
        self,
        expected: str | list[str],
        case_sensitive: bool = False,
    ):
        self.expected = [expected] if isinstance(expected, str) else expected
        self.case_sensitive = case_sensitive

    def evaluate(self, output: str, context: dict[str, Any]) -> dict[str, Any]:
        check_output = output if self.case_sensitive else output.lower()

        results = {}
        for exp in self.expected:
            check_exp = exp if self.case_sensitive else exp.lower()
            results[exp] = check_exp in check_output

        all_found = all(results.values())

        return {
            "type": "contains",
            "passed": all_found,
            "score": 10.0 if all_found else 0.0,
            "found": results,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "contains",
            "expected": self.expected,
            "case_sensitive": self.case_sensitive,
        }
