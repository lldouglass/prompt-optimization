"""Test the enhanced optimizer with few-shot research on the market analysis prompt."""

import json
from agents.optimizer import PromptOptimizer

# The market analysis prompt from earlier
MARKET_ANALYSIS_PROMPT = """You are a senior market research analyst specializing in developer tools and AI/ML infrastructure. Conduct a thorough market analysis for PromptLab, a B2B SaaS platform for LLM operations (LLMOps).

## Product Overview

PromptLab helps companies building AI-powered products by providing:
1. **Request Logging** - Automatic capture of all LLM API calls with full request/response data, token counts, latency, and cost tracking
2. **Prompt Optimization** - AI-powered analysis and improvement of prompts using proven prompt engineering techniques
3. **Quality Scoring** - Automatic evaluation of LLM responses for quality and relevance
4. **A/B Testing** - Compare prompt variations to find the best performing version

**Pricing Tiers:**
- Free: 1,000 requests/month, 10 optimizations
- Pro ($99/mo): 50,000 requests/month, 100 optimizations
- Team ($299/mo): 500,000 requests/month, unlimited optimizations
- Enterprise: Custom pricing

## Analysis Required

### 1. Market Size & Growth
- Estimate the Total Addressable Market (TAM) for LLMOps tools
- Estimate the Serviceable Addressable Market (SAM) for prompt optimization specifically
- Project market growth rate for 2024-2028
- Identify key growth drivers

### 2. Competitor Analysis
Analyze direct and indirect competitors including:
- LangSmith (LangChain)
- Weights & Biases (Prompts)
- Helicone
- PromptLayer
- Humanloop
- Arize AI
- Portkey

For each competitor, assess:
- Core features and differentiators
- Pricing model
- Target customer segment
- Strengths and weaknesses
- Market positioning

### 3. Target Customer Segments
Identify and prioritize customer segments:
- Company size (startup, SMB, enterprise)
- Industry verticals most likely to adopt
- Job titles/roles of buyers and users
- Use cases and pain points by segment
- Willingness to pay by segment

### 4. Competitive Positioning
- What is PromptLab's unique value proposition?
- Where should PromptLab position against competitors?
- What features would create the strongest differentiation?
- Blue ocean opportunities in the market

### 5. Go-to-Market Strategy
Recommend:
- Primary customer acquisition channels
- Content marketing topics that would resonate
- Partnership opportunities
- Community building strategies
- Pricing optimization suggestions

### 6. Risks & Challenges
- Market risks (commoditization, platform risk from OpenAI/Anthropic)
- Competitive threats
- Technical challenges
- Regulatory considerations

### 7. Opportunities
- Emerging trends to capitalize on
- Adjacent markets to expand into
- Feature gaps in competitor offerings
- Timing advantages

## Output Format

Provide your analysis in a structured report with:
1. Executive Summary (key findings and recommendations)
2. Detailed analysis for each section above
3. Strategic recommendations prioritized by impact and effort
4. 90-day action plan for market entry

Use specific data points, percentages, and dollar figures where possible. Cite reasonable assumptions when exact data isn't available."""

TASK_DESCRIPTION = "Conduct a comprehensive market analysis for a B2B SaaS LLMOps platform, including market sizing, competitor analysis, customer segmentation, and go-to-market strategy recommendations."


def main():
    print("=" * 80)
    print("TESTING ENHANCED PROMPT OPTIMIZER WITH FEW-SHOT RESEARCH")
    print("=" * 80)

    optimizer = PromptOptimizer(model="gpt-5-mini")

    print("\n[Step 1] Analyzing prompt...")
    analysis = optimizer.analyze(MARKET_ANALYSIS_PROMPT, TASK_DESCRIPTION)

    print(f"\nAnalysis Results:")
    print(f"  Overall Quality: {analysis.overall_quality}")
    print(f"  Issues Found: {len(analysis.issues)}")
    for issue in analysis.issues:
        print(f"    - [{issue['severity'].upper()}] {issue['category']}: {issue['description']}")

    print(f"\n  Needs Few-Shot Examples: {analysis.needs_few_shot_examples()}")

    if analysis.needs_few_shot_examples():
        print("\n[Step 2] Researching few-shot examples...")
        few_shot = optimizer.research_few_shot_examples(MARKET_ANALYSIS_PROMPT, TASK_DESCRIPTION)

        print(f"\nFew-Shot Research Results:")
        print(f"  Number of Examples: {len(few_shot.examples)}")
        print(f"  Format Recommendation: {few_shot.format_recommendation}")
        print(f"  Research Notes: {few_shot.research_notes}")

        print("\n  Examples:")
        for i, ex in enumerate(few_shot.examples, 1):
            print(f"\n  --- Example {i} ---")
            print(f"  Input: {ex.input[:200]}..." if len(ex.input) > 200 else f"  Input: {ex.input}")
            print(f"  Output: {ex.output[:300]}..." if len(ex.output) > 300 else f"  Output: {ex.output}")
            print(f"  Rationale: {ex.rationale}")

    print("\n[Step 3] Running full optimization (this may take a minute)...")
    result = optimizer.optimize(
        MARKET_ANALYSIS_PROMPT,
        TASK_DESCRIPTION,
        sample_inputs=["Analyze the market for PromptLab"]
    )

    print("\n" + "=" * 80)
    print("OPTIMIZATION RESULTS")
    print("=" * 80)

    print(f"\nScore Improvement: {result.original_score:.1f} -> {result.optimized_score:.1f}")
    print(f"Improvement: +{result.optimized_score - result.original_score:.1f}")

    print(f"\nImprovements Made:")
    for imp in result.improvements:
        print(f"  - {imp}")

    print(f"\nReasoning: {result.reasoning}")

    print("\n" + "-" * 80)
    print("OPTIMIZED PROMPT (with few-shot examples)")
    print("-" * 80)
    print(result.optimized_prompt)

    # Save full results to file
    with open("optimization_result.json", "w") as f:
        json.dump(result.to_dict(), f, indent=2)
    print("\n\nFull results saved to optimization_result.json")


if __name__ == "__main__":
    main()
