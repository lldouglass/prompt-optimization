"""
Web Researcher - Searches the web for few-shot examples and prompt patterns.

Uses Tavily API for high-quality search results optimized for LLM consumption.
"""

import json
import re
from dataclasses import dataclass, field
from typing import List, Optional
import httpx
import os

import llm.client as llm_client


@dataclass
class WebSource:
    """A source from web search."""
    url: str
    title: str
    content: str
    relevance_score: float = 0.0


@dataclass
class WebResearchResult:
    """Results from web research for few-shot examples."""
    examples: List[dict]  # {input, output, rationale}
    sources: List[WebSource]
    search_queries: List[str]
    research_notes: str


GENERATE_QUERIES_PROMPT = """<role>
You are a search query specialist helping find real-world examples and patterns for prompt engineering.
</role>

<task>
Generate 2-3 targeted search queries to find:
1. Official documentation examples for this type of task
2. GitHub repositories with similar prompt patterns
3. Best practices and real-world examples

Task being optimized: {task_description}

Original prompt context:
{prompt_snippet}
</task>

<format>
Return ONLY a JSON array of search queries:
["query 1", "query 2", "query 3"]

Make queries specific and likely to return useful prompt examples.
</format>"""


SYNTHESIZE_EXAMPLES_PROMPT = """<role>
You are an expert at extracting and synthesizing few-shot examples from documentation and code.
</role>

<task>
Based on the search results below, create 2-4 high-quality few-shot examples for this task:

Task: {task_description}

Search Results:
{search_results}
</task>

<guidelines>
1. Extract REAL patterns from the search results - don't fabricate
2. Adapt examples to fit the specific task
3. Include diverse cases: simple, complex, edge cases
4. Use consistent Input/Output format
5. If search results lack examples, create minimal examples based on documented patterns
</guidelines>

<format>
Return ONLY a valid JSON object:
{{
  "examples": [
    {{
      "input": "example input/query",
      "output": "expected output/response",
      "rationale": "why this example is useful",
      "source": "which search result inspired this"
    }}
  ],
  "format_recommendation": "Input: {{input}}\\nOutput: {{output}}",
  "research_notes": "summary of what was found in search results"
}}
</format>"""


class WebResearcher:
    """
    Researches few-shot examples using web search.

    Uses Tavily API when available for high-quality results,
    provides graceful degradation without API key.
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.tavily_api_key = os.environ.get("TAVILY_API_KEY")

    @property
    def is_available(self) -> bool:
        """Check if web research is available (Tavily key configured)."""
        return bool(self.tavily_api_key)

    async def research_examples(
        self,
        prompt_template: str,
        task_description: str
    ) -> WebResearchResult:
        """
        Research few-shot examples from the web.

        Args:
            prompt_template: The original prompt being optimized
            task_description: What the prompt should accomplish

        Returns:
            WebResearchResult with examples, sources, and notes
        """
        if not self.is_available:
            return WebResearchResult(
                examples=[],
                sources=[],
                search_queries=[],
                research_notes="Web research unavailable - Tavily API key not configured"
            )

        # Step 1: Generate targeted search queries
        search_queries = await self._generate_search_queries(
            prompt_template[:500],  # Limit context size
            task_description
        )

        if not search_queries:
            search_queries = [
                f"{task_description} prompt example",
                f"{task_description} few-shot template"
            ]

        # Step 2: Execute searches
        all_results = []
        all_sources = []

        for query in search_queries[:3]:  # Max 3 searches for cost control
            results, sources = await self._tavily_search(query)
            all_results.extend(results)
            all_sources.extend(sources)

        if not all_results:
            return WebResearchResult(
                examples=[],
                sources=[],
                search_queries=search_queries,
                research_notes="No relevant results found from web search"
            )

        # Step 3: Synthesize examples from search results
        examples, notes = await self._synthesize_examples(
            task_description,
            all_results
        )

        return WebResearchResult(
            examples=examples,
            sources=all_sources[:5],  # Limit sources returned
            search_queries=search_queries,
            research_notes=notes
        )

    async def _generate_search_queries(
        self,
        prompt_snippet: str,
        task_description: str
    ) -> List[str]:
        """Generate targeted search queries for finding examples."""
        prompt = GENERATE_QUERIES_PROMPT.format(
            task_description=task_description,
            prompt_snippet=prompt_snippet
        )

        messages = [{"role": "user", "content": prompt}]
        result = llm_client.chat(self.model, messages)

        try:
            # Try to parse as JSON array
            json_match = re.search(r'\[[\s\S]*\]', result)
            if json_match:
                queries = json.loads(json_match.group())
                if isinstance(queries, list):
                    return [q for q in queries if isinstance(q, str)][:3]
        except (json.JSONDecodeError, AttributeError):
            pass

        # Fallback: generate basic queries
        return [
            f"{task_description} prompt template example",
            f"{task_description} LLM few-shot"
        ]

    async def _tavily_search(self, query: str) -> tuple[List[str], List[WebSource]]:
        """
        Search using Tavily API.

        Returns:
            Tuple of (result_texts, sources)
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": self.tavily_api_key,
                        "query": query,
                        "search_depth": "basic",  # Use basic for cost efficiency
                        "include_answer": True,
                        "include_raw_content": False,
                        "max_results": 5
                    },
                    timeout=15.0
                )

                if response.status_code == 200:
                    data = response.json()
                    results = []
                    sources = []

                    # Include the AI-generated answer if available
                    if data.get("answer"):
                        results.append(f"Summary: {data['answer']}")

                    # Process search results
                    for item in data.get("results", []):
                        content = item.get("content", "")
                        if content:
                            results.append(content)
                            sources.append(WebSource(
                                url=item.get("url", ""),
                                title=item.get("title", ""),
                                content=content[:500],  # Truncate for response
                                relevance_score=item.get("score", 0.0)
                            ))

                    return results, sources
                else:
                    # Log error but don't fail
                    print(f"Tavily search failed with status {response.status_code}")

        except Exception as e:
            print(f"Tavily search error: {str(e)}")

        return [], []

    async def _synthesize_examples(
        self,
        task_description: str,
        search_results: List[str]
    ) -> tuple[List[dict], str]:
        """
        Use LLM to synthesize few-shot examples from search results.

        Returns:
            Tuple of (examples, research_notes)
        """
        # Combine and truncate search results
        combined_results = "\n\n---\n\n".join(search_results[:10])
        if len(combined_results) > 4000:
            combined_results = combined_results[:4000] + "...[truncated]"

        prompt = SYNTHESIZE_EXAMPLES_PROMPT.format(
            task_description=task_description,
            search_results=combined_results
        )

        messages = [{"role": "user", "content": prompt}]
        result = llm_client.chat(self.model, messages)

        try:
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                data = json.loads(json_match.group())
                examples = data.get("examples", [])
                notes = data.get("research_notes", "Examples synthesized from web search")
                return examples, notes
        except (json.JSONDecodeError, AttributeError):
            pass

        return [], "Failed to synthesize examples from search results"


# Convenience function for quick access
async def research_few_shot_examples(
    prompt_template: str,
    task_description: str,
    model: str = "gpt-4o-mini"
) -> WebResearchResult:
    """
    Research few-shot examples from the web.

    Args:
        prompt_template: The prompt being optimized
        task_description: What the prompt should accomplish
        model: LLM model to use for query generation and synthesis

    Returns:
        WebResearchResult with examples and sources
    """
    researcher = WebResearcher(model=model)
    return await researcher.research_examples(prompt_template, task_description)
