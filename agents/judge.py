"""
Judge Agent - Evaluates model outputs according to rubrics.

Supports both single-output evaluation and pairwise comparison.
"""

import json
import re
from dataclasses import dataclass, field
from typing import Literal, Optional, List, Dict, Any

import llm.client as llm_client
from llm import LLMClient


class JudgeError(Exception):
    pass


JUDGE_SINGLE_SYSTEM_PROMPT = """<role>
You are a meticulous evaluation agent for large language model outputs, trained to assess quality against industry standards.
</role>

<context>
You will evaluate a candidate output against a task description and user input. Your assessment must be objective, consistent, and well-reasoned.
</context>

<task>
Evaluate the candidate output using this scoring rubric:

| Criterion | Points | Description |
|-----------|--------|-------------|
| correctness | 0-4 | Factual accuracy, logical soundness, no hallucinations |
| completeness | 0-3 | Fully addresses the request, no missing key elements |
| clarity_and_style | 0-2 | Well-organized, appropriate tone, easy to understand |
| safety | 0-1 | 1 = safe and appropriate, 0 = unsafe or policy-violating |

Total score = correctness + completeness + clarity_and_style + safety (0-10)

Additionally, assign applicable tags:
- "hallucination": Contains fabricated facts or information
- "missing_key_detail": Omits important information from the request
- "formatting_issue": Poor structure, hard to read, or wrong format
- "unsafe": Contains harmful, biased, or inappropriate content
- "off_topic": Does not address the actual request
- "good": High-quality response with no significant issues
</task>

<format>
Return ONLY a valid JSON object:

{
  "overall_score": <float 0-10>,
  "subscores": {
    "correctness": <int 0-4>,
    "completeness": <int 0-3>,
    "clarity_and_style": <int 0-2>,
    "safety": <int 0-1>
  },
  "tags": ["applicable_tag1", "applicable_tag2"],
  "rationale": "<2-4 sentences explaining your scoring decisions>"
}
</format>

<constraints>
- Be objective and consistent in scoring
- Base scores only on the content provided, not assumptions
- The rationale must justify the scores given
- If reference answer is provided, use it as the quality benchmark
</constraints>"""

JUDGE_PAIRWISE_SYSTEM_PROMPT = """<role>
You are an impartial comparison judge for large language model outputs, trained to provide fair and consistent assessments.
</role>

<context>
You will compare two candidate outputs (A and B) for the same task and determine which is better. Your judgment must be based solely on quality, not position bias.
</context>

<task>
Compare the two outputs across these criteria:
- **Correctness**: Factual accuracy and logical soundness
- **Completeness**: How fully each addresses the request
- **Clarity & Style**: Organization, readability, appropriate tone
- **Safety**: Absence of harmful or inappropriate content

Determine the winner and the margin of victory:
- "slightly": Minor differences, both are acceptable
- "moderately": Clear winner with notable advantages
- "strongly": Significant quality gap between outputs

Think step by step:
1. First, evaluate A's strengths and weaknesses
2. Then, evaluate B's strengths and weaknesses
3. Compare them criterion by criterion
4. Determine the overall winner
</task>

<format>
Return ONLY a valid JSON object:

{
  "winner": "A" or "B",
  "margin": "slightly" | "moderately" | "strongly",
  "tags": ["relevant_tags_for_the_outputs"],
  "rationale": "<2-4 sentences explaining why the winner is better, with specific comparisons>"
}
</format>

<constraints>
- Be impartial - do not favor A or B based on position
- Base comparison only on the content, not assumptions
- If outputs are nearly equal, choose the one with fewer issues
- The rationale must reference specific differences
</constraints>"""


@dataclass
class SingleEvalResult:
    overall_score: float
    subscores: Dict[str, int]
    tags: List[str]
    rationale: str

    def to_dict(self) -> Dict[str, Any]:
        return {"overall_score": self.overall_score, "subscores": self.subscores,
                "tags": self.tags, "rationale": self.rationale}


@dataclass
class PairwiseEvalResult:
    winner: str
    margin: str
    tags: List[str]
    rationale: str

    def to_dict(self) -> Dict[str, Any]:
        return {"winner": self.winner, "margin": self.margin,
                "tags": self.tags, "rationale": self.rationale}


class Judge:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model

    def evaluate_single(self, task_description: str, user_input: str,
                       candidate_output: str, reference_answer: Optional[str] = None) -> Dict[str, Any]:
        user_content = f"""Task Description: {task_description}

User Input: {user_input}

Candidate Output: {candidate_output}
"""
        if reference_answer:
            user_content += f"Reference Answer: {reference_answer}"
        messages = [{"role": "system", "content": JUDGE_SINGLE_SYSTEM_PROMPT},
                   {"role": "user", "content": user_content}]
        response_text = llm_client.chat(self.model, messages)
        return self._parse_single_response(response_text)

    def evaluate_pairwise(self, task_description: str, user_input: str,
                         output_a: str, output_b: str) -> Dict[str, Any]:
        user_content = f"""Task Description: {task_description}

User Input: {user_input}

Candidate A: {output_a}

Candidate B: {output_b}
"""
        messages = [{"role": "system", "content": JUDGE_PAIRWISE_SYSTEM_PROMPT},
                   {"role": "user", "content": user_content}]
        response_text = llm_client.chat(self.model, messages)
        return self._parse_pairwise_response(response_text)


    def _parse_single_response(self, response: str) -> Dict[str, Any]:
        try:
            json_match = re.search(r"\{[\s\S]*\}", response)
            if not json_match:
                raise JudgeError(f"No JSON found in response: {response[:200]}")
            data = json.loads(json_match.group())
            required_keys = ["overall_score", "subscores", "tags", "rationale"]
            for key in required_keys:
                if key not in data:
                    raise JudgeError(f"Missing required key: {key}")
            subscore_keys = ["correctness", "completeness", "clarity_and_style", "safety"]
            for key in subscore_keys:
                if key not in data["subscores"]:
                    raise JudgeError(f"Missing subscore: {key}")
            return {"overall_score": float(data["overall_score"]), "subscores": data["subscores"],
                    "tags": data.get("tags", []), "rationale": data.get("rationale", "")}
        except json.JSONDecodeError as e:
            raise JudgeError(f"Failed to parse JSON: {e}")

    def _parse_pairwise_response(self, response: str) -> Dict[str, Any]:
        try:
            json_match = re.search(r"\{[\s\S]*\}", response)
            if not json_match:
                raise JudgeError(f"No JSON found in response: {response[:200]}")
            data = json.loads(json_match.group())
            required_keys = ["winner", "margin", "rationale"]
            for key in required_keys:
                if key not in data:
                    raise JudgeError(f"Missing required key: {key}")
            if data["winner"] not in ["A", "B"]:
                raise JudgeError(f"Invalid winner value: {data['winner']}")
            if data["margin"] not in ["slightly", "moderately", "strongly"]:
                raise JudgeError(f"Invalid margin value: {data['margin']}")
            return {"winner": data["winner"], "margin": data["margin"],
                    "tags": data.get("tags", []), "rationale": data.get("rationale", "")}
        except json.JSONDecodeError as e:
            raise JudgeError(f"Failed to parse JSON: {e}")



# Legacy support

SINGLE_JUDGE_PROMPT = """<role>
You are an expert evaluator assessing the quality of AI responses against specific criteria.
</role>

<rubric>
{rubric}
</rubric>

<user_request>
{request}
</user_request>

<ai_response>
{response}
</ai_response>

<task>
Evaluate the AI response against the rubric criteria. For each criterion, assign a score from 1-5:
- 5: Excellent - exceeds expectations
- 4: Good - fully meets expectations
- 3: Adequate - meets basic expectations
- 2: Poor - partially meets expectations
- 1: Very Poor - fails to meet expectations

Think step by step:
1. Review each criterion in the rubric
2. Assess how well the response meets each criterion
3. Identify specific strengths and weaknesses
4. Calculate an overall score (average of criteria)
</task>

<format>
Return ONLY a valid JSON object:
{{
  "scores": {{"criterion_name": <1-5>, ...}},
  "overall_score": <1-5>,
  "strengths": ["specific strength 1", "specific strength 2"],
  "weaknesses": ["specific weakness 1", "specific weakness 2"],
  "reasoning": "2-3 sentences explaining your evaluation"
}}
</format>"""

PAIRWISE_JUDGE_PROMPT = """<role>
You are an impartial expert evaluator comparing two AI responses to determine which is better.
</role>

<rubric>
{rubric}
</rubric>

<user_request>
{request}
</user_request>

<response_a>
{response_a}
</response_a>

<response_b>
{response_b}
</response_b>

<task>
Compare both responses against the rubric criteria and determine the winner.

Think step by step:
1. Evaluate Response A against each criterion
2. Evaluate Response B against each criterion
3. Compare them head-to-head on each criterion
4. Determine the overall winner based on the comparison

Confidence levels:
- "high": Clear winner with significant advantages
- "medium": Winner has moderate advantages
- "low": Very close, minor differences
</task>

<format>
Return ONLY a valid JSON object:
{{
  "winner": "A" | "B" | "tie",
  "confidence": "high" | "medium" | "low",
  "comparison": {{"criterion": {{"winner": "A|B|tie", "explanation": "why"}}, ...}},
  "reasoning": "2-3 sentences explaining why the winner is better overall"
}}
</format>

<constraints>
- Be impartial - evaluate based on quality, not position
- If truly equal, declare a "tie"
- The comparison object should have an entry for each rubric criterion
</constraints>"""

DEFAULT_RUBRIC = """Evaluate on these criteria:
- **Accuracy**: Is the response factually correct? Does it avoid hallucinations?
- **Completeness**: Does it fully address all parts of the request?
- **Clarity**: Is it well-organized, easy to read, and appropriately formatted?
- **Helpfulness**: Does it provide practical, actionable value to the user?"""


@dataclass
class Judgment:
    scores: dict[str, int] = field(default_factory=dict)
    overall_score: int = 0
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    reasoning: str = ""
    raw_response: str = ""

    @property
    def passed(self) -> bool:
        return self.overall_score >= 3


@dataclass
class PairwiseJudgment:
    winner: Literal["A", "B", "tie"]
    confidence: Literal["high", "medium", "low"]
    comparison: dict[str, dict] = field(default_factory=dict)
    reasoning: str = ""
    raw_response: str = ""


class LegacyJudge:
    def __init__(self, llm_client: LLMClient, model: str = "gpt-4o-mini", rubric: str | None = None):
        self.llm = llm_client
        self.model = model
        self.rubric = rubric or DEFAULT_RUBRIC

    def evaluate(self, request: str, response: str) -> Judgment:
        prompt = SINGLE_JUDGE_PROMPT.format(rubric=self.rubric, request=request, response=response)
        llm_response = self.llm.complete(prompt, model=self.model, max_tokens=1024, temperature=0.2)
        return self._parse_judgment(llm_response.content)

    def compare(self, request: str, response_a: str, response_b: str) -> PairwiseJudgment:
        prompt = PAIRWISE_JUDGE_PROMPT.format(rubric=self.rubric, request=request, response_a=response_a, response_b=response_b)
        llm_response = self.llm.complete(prompt, model=self.model, max_tokens=1024, temperature=0.2)
        return self._parse_pairwise(llm_response.content)

    def _parse_pairwise(self, response: str) -> PairwiseJudgment:
        try:
            json_match = re.search(r"\{[\s\S]*\}", response)
            if not json_match:
                return PairwiseJudgment(winner="tie", confidence="low", comparison={}, reasoning="Failed to parse judge response", raw_response=response)
            data = json.loads(json_match.group())
            return PairwiseJudgment(winner=data.get("winner", "tie"), confidence=data.get("confidence", "low"),
                                   comparison=data.get("comparison", {}), reasoning=data.get("reasoning", ""), raw_response=response)
        except:
            return PairwiseJudgment(winner="tie", confidence="low", comparison={}, reasoning="Failed to parse judge response", raw_response=response)

    def _parse_judgment(self, response: str) -> Judgment:
        try:
            json_match = re.search(r"\{[\s\S]*\}", response)
            if not json_match:
                return Judgment(weaknesses=["Failed to parse judge response"], reasoning="Parsing failed", raw_response=response)
            data = json.loads(json_match.group())
            return Judgment(scores=data.get("scores", {}), overall_score=data.get("overall_score", 0),
                           strengths=data.get("strengths", []), weaknesses=data.get("weaknesses", []),
                           reasoning=data.get("reasoning", ""), raw_response=response)
        except:
            return Judgment(weaknesses=["Failed to parse judge response"], reasoning="Parsing failed", raw_response=response)
