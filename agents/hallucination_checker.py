"""
Hallucination Checker - Verifies factual claims in LLM responses using web search.
"""

import json
import re
from dataclasses import dataclass
from typing import List, Optional
import httpx

import llm.client as llm_client


EXTRACT_CLAIMS_PROMPT = """<role>
You are a fact extraction agent. Your job is to identify specific factual claims that can be verified.
</role>

<task>
Extract verifiable factual claims from the following response. Focus on:
- Statistics and numbers
- Dates and historical events
- Scientific facts
- Named entities (people, companies, products)
- Technical specifications
- Quotes or attributed statements

Do NOT extract:
- Opinions or subjective statements
- General knowledge that's commonly accepted
- Vague or non-specific claims
- The user's own statements from the request
</task>

<request>
{request}
</request>

<response>
{response}
</response>

<format>
Return ONLY a valid JSON object:
{{
  "claims": [
    {{
      "claim": "The specific factual claim",
      "search_query": "A good search query to verify this claim"
    }}
  ]
}}

If there are no verifiable factual claims, return: {{"claims": []}}
Limit to the 5 most important claims.
</format>"""


VERIFY_CLAIM_PROMPT = """<role>
You are a fact-checking agent that determines if a claim is supported by search results.
</role>

<claim>
{claim}
</claim>

<search_results>
{search_results}
</search_results>

<task>
Based on the search results, determine if the claim is:
- "verified": The search results clearly support this claim
- "contradicted": The search results clearly contradict this claim
- "unverified": Cannot determine from search results (insufficient or unclear evidence)

Be conservative - only mark as "verified" if there's clear supporting evidence.
</task>

<format>
Return ONLY a valid JSON object:
{{
  "status": "verified" | "contradicted" | "unverified",
  "evidence": "Brief explanation of what the search results say",
  "source": "The most relevant source URL if available"
}}
</format>"""


@dataclass
class ClaimVerification:
    claim: str
    status: str  # "verified", "contradicted", "unverified"
    evidence: str
    source: Optional[str] = None


@dataclass
class HallucinationReport:
    has_hallucinations: bool
    verified_claims: List[ClaimVerification]
    contradicted_claims: List[ClaimVerification]
    unverified_claims: List[ClaimVerification]
    summary: str

    def to_dict(self) -> dict:
        return {
            "has_hallucinations": self.has_hallucinations,
            "verified_claims": [
                {"claim": c.claim, "status": c.status, "evidence": c.evidence, "source": c.source}
                for c in self.verified_claims
            ],
            "contradicted_claims": [
                {"claim": c.claim, "status": c.status, "evidence": c.evidence, "source": c.source}
                for c in self.contradicted_claims
            ],
            "unverified_claims": [
                {"claim": c.claim, "status": c.status, "evidence": c.evidence, "source": c.source}
                for c in self.unverified_claims
            ],
            "summary": self.summary,
        }


class HallucinationChecker:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model

    async def check(self, request: str, response: str) -> HallucinationReport:
        """Check a response for hallucinations by extracting and verifying claims."""

        # Step 1: Extract factual claims
        claims = await self._extract_claims(request, response)

        if not claims:
            return HallucinationReport(
                has_hallucinations=False,
                verified_claims=[],
                contradicted_claims=[],
                unverified_claims=[],
                summary="No verifiable factual claims found in the response."
            )

        # Step 2: Verify each claim using web search
        verified = []
        contradicted = []
        unverified = []

        for claim_data in claims:
            verification = await self._verify_claim(claim_data["claim"], claim_data["search_query"])

            if verification.status == "verified":
                verified.append(verification)
            elif verification.status == "contradicted":
                contradicted.append(verification)
            else:
                unverified.append(verification)

        # Step 3: Generate summary
        has_hallucinations = len(contradicted) > 0

        if has_hallucinations:
            summary = f"Found {len(contradicted)} potentially false claim(s) that contradict search results."
        elif len(unverified) > 0:
            summary = f"Verified {len(verified)} claim(s). {len(unverified)} claim(s) could not be verified."
        else:
            summary = f"All {len(verified)} factual claim(s) were verified."

        return HallucinationReport(
            has_hallucinations=has_hallucinations,
            verified_claims=verified,
            contradicted_claims=contradicted,
            unverified_claims=unverified,
            summary=summary
        )

    async def _extract_claims(self, request: str, response: str) -> List[dict]:
        """Extract verifiable factual claims from the response."""
        prompt = EXTRACT_CLAIMS_PROMPT.format(request=request, response=response)

        messages = [{"role": "user", "content": prompt}]
        result = llm_client.chat(self.model, messages)

        try:
            json_match = re.search(r"\{[\s\S]*\}", result)
            if json_match:
                data = json.loads(json_match.group())
                return data.get("claims", [])
        except (json.JSONDecodeError, AttributeError):
            pass

        return []

    async def _verify_claim(self, claim: str, search_query: str) -> ClaimVerification:
        """Verify a single claim using web search."""

        # Perform web search
        search_results = await self._web_search(search_query)

        if not search_results:
            return ClaimVerification(
                claim=claim,
                status="unverified",
                evidence="Could not perform web search to verify this claim.",
                source=None
            )

        # Use LLM to analyze search results
        prompt = VERIFY_CLAIM_PROMPT.format(claim=claim, search_results=search_results)
        messages = [{"role": "user", "content": prompt}]
        result = llm_client.chat(self.model, messages)

        try:
            json_match = re.search(r"\{[\s\S]*\}", result)
            if json_match:
                data = json.loads(json_match.group())
                return ClaimVerification(
                    claim=claim,
                    status=data.get("status", "unverified"),
                    evidence=data.get("evidence", ""),
                    source=data.get("source")
                )
        except (json.JSONDecodeError, AttributeError):
            pass

        return ClaimVerification(
            claim=claim,
            status="unverified",
            evidence="Failed to analyze search results.",
            source=None
        )

    async def _web_search(self, query: str) -> str:
        """Perform a web search and return formatted results."""
        try:
            # Use DuckDuckGo instant answer API (no API key needed)
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.duckduckgo.com/",
                    params={
                        "q": query,
                        "format": "json",
                        "no_html": 1,
                        "skip_disambig": 1
                    },
                    timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()
                    results = []

                    # Get abstract
                    if data.get("Abstract"):
                        results.append(f"Summary: {data['Abstract']}")
                        if data.get("AbstractURL"):
                            results.append(f"Source: {data['AbstractURL']}")

                    # Get related topics
                    for topic in data.get("RelatedTopics", [])[:3]:
                        if isinstance(topic, dict) and topic.get("Text"):
                            results.append(f"- {topic['Text']}")

                    if results:
                        return "\n".join(results)

                    # Fallback: return a note that we couldn't find specific results
                    return f"No specific results found for: {query}"

        except Exception as e:
            return f"Search failed: {str(e)}"

        return ""
