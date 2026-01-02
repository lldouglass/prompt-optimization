"""
Multi-Agent System - No Framework Required

This shows how to coordinate multiple agents without LangGraph/CrewAI.
Each agent has a specific role and they pass work to each other.

Key insight: "Multi-agent" is just calling different system prompts
in sequence, passing the output of one as input to the next.
"""

# json module for parsing (not used here but often needed)
import json

# os module for reading environment variables
import os

# dataclass is a Python decorator that auto-generates __init__, __repr__, etc.
# It's a clean way to define simple classes that hold data
from dataclasses import dataclass

# OpenAI client for making API calls
from openai import OpenAI

# Create the OpenAI client with API key from environment
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


# =============================================================================
# Define Agents (just system prompts + configs)
# =============================================================================

# @dataclass automatically creates __init__ and other methods
# This is a cleaner way to define a simple class that holds data
@dataclass
class Agent:
    """
    An Agent is just a container for:
    - name: identifier for logging
    - role: what type of work this agent does
    - system_prompt: the instructions that define agent behavior
    - model: which LLM model to use
    """
    name: str           # e.g., "Researcher"
    role: str           # e.g., "research"
    system_prompt: str  # The full system prompt
    model: str = "gpt-4o-mini"  # Default model (can be overridden)


# Define the RESEARCHER agent
# This agent's job is to find and gather information
RESEARCHER = Agent(
    name="Researcher",  # Display name for logging
    role="research",    # Role identifier

    # The system prompt defines EVERYTHING about how this agent behaves
    # Notice how it explicitly states what the agent should and should NOT do
    system_prompt="""You are a Research Agent.

Your job:
- Find and gather factual information
- Cite sources when possible
- Be thorough but concise

You ONLY research. You DO NOT:
- Write final reports (that's the Writer's job)
- Make recommendations
- Analyze data

When done researching, summarize your findings in bullet points."""
)

# Define the WRITER agent
# This agent's job is to take research and write polished content
WRITER = Agent(
    name="Writer",
    role="write",

    system_prompt="""You are a Writing Agent.

Your job:
- Take research findings and write polished content
- Structure information clearly
- Use professional tone

You ONLY write. You DO NOT:
- Do research (that's already done)
- Make up facts
- Add information not provided

Write based solely on the research provided to you."""
)

# Define the REVIEWER agent
# This agent's job is to check quality and approve or request revisions
REVIEWER = Agent(
    name="Reviewer",
    role="review",

    system_prompt="""You are a Review Agent.

Your job:
- Check content for accuracy and clarity
- Suggest improvements
- Approve when ready

Respond with either:
1. "APPROVED" if the content is good
2. "REVISE: [specific feedback]" if changes are needed"""
)


# =============================================================================
# Simple agent runner (same loop concept, but simpler since no tools)
# =============================================================================

def run_single_agent(agent: Agent, task: str, context: str = "") -> str:
    """
    Run a single agent on a task.

    Args:
        agent: The Agent to run (contains system_prompt, model, etc.)
        task: What we want the agent to do
        context: Optional context from previous agents (e.g., research findings)

    Returns:
        The agent's response as a string
    """

    # Build the messages list for the API call
    messages = [
        # System message sets the agent's behavior
        {"role": "system", "content": agent.system_prompt},
    ]

    # If we have context from a previous agent, include it
    if context:
        # Combine context and task into one user message
        messages.append({
            "role": "user",
            "content": f"Context:\n{context}\n\nTask: {task}"
        })
    else:
        # Just the task, no context
        messages.append({
            "role": "user",
            "content": task
        })

    # Call the OpenAI API
    # This is simpler than the tool-calling version because we're just
    # getting text responses - no tool execution needed
    response = client.chat.completions.create(
        model=agent.model,      # Which model to use
        messages=messages,      # The conversation
        temperature=0.7         # Controls randomness (0=deterministic, 1=creative)
    )

    # Extract and return just the text content
    return response.choices[0].message.content


# =============================================================================
# Multi-Agent Workflow (the "orchestrator")
# =============================================================================

def research_and_write(topic: str, verbose: bool = True) -> str:
    """
    Coordinate multiple agents to research and write about a topic.

    This is the "orchestrator" function - it decides which agent to call,
    in what order, and how to pass data between them.

    Flow: Researcher -> Writer -> Reviewer -> (loop back to Writer if needed)

    Args:
        topic: What to research and write about
        verbose: If True, print progress updates

    Returns:
        The final approved content
    """

    # Print header if verbose
    if verbose:
        print(f"\n{'='*60}")
        print(f"TOPIC: {topic}")
        print("=" * 60)

    # =========================================================================
    # STEP 1: Research
    # Call the Researcher agent to gather information
    # =========================================================================
    if verbose:
        print(f"\n[{RESEARCHER.name}] Researching...")

    # Run the researcher agent
    # Note: No context parameter because this is the first step
    research = run_single_agent(
        RESEARCHER,  # Which agent to use
        f"Research this topic thoroughly: {topic}"  # The task
    )

    if verbose:
        # Print first 200 characters of research (truncated for readability)
        print(f"Research complete:\n{research[:200]}...")

    # =========================================================================
    # STEP 2: Write
    # Call the Writer agent to create content based on the research
    # =========================================================================
    if verbose:
        print(f"\n[{WRITER.name}] Writing...")

    # Run the writer agent
    # Pass the research as context so the writer can use it
    draft = run_single_agent(
        WRITER,
        f"Write a clear, informative piece about: {topic}",
        context=f"Research findings:\n{research}"  # Pass research as context
    )

    if verbose:
        print(f"Draft complete:\n{draft[:200]}...")

    # =========================================================================
    # STEP 3: Review (with revision loop)
    # Call the Reviewer agent to check quality
    # If not approved, send back to Writer for revision
    # =========================================================================

    # Maximum number of revision attempts (prevents infinite loops)
    max_revisions = 3

    # Loop for revision cycles
    for revision in range(max_revisions):

        if verbose:
            print(f"\n[{REVIEWER.name}] Reviewing (attempt {revision + 1})...")

        # Run the reviewer agent
        review = run_single_agent(
            REVIEWER,
            "Review this content for accuracy and clarity.",
            context=f"Content to review:\n{draft}"  # Pass the draft to review
        )

        if verbose:
            print(f"Review result: {review[:100]}...")

        # Check if the reviewer approved the content
        # We look for "APPROVED" in the response (case-insensitive)
        if "APPROVED" in review.upper():

            if verbose:
                print("\n[APPROVED] Content passed review!")

            # Return the approved draft
            return draft

        # =====================================================================
        # REVISION NEEDED
        # Send the draft back to the Writer with the reviewer's feedback
        # =====================================================================
        if verbose:
            print(f"\n[{WRITER.name}] Revising based on feedback...")

        # Run the writer again with the feedback
        draft = run_single_agent(
            WRITER,
            "Revise the content based on this feedback.",
            context=f"Original content:\n{draft}\n\nFeedback:\n{review}"
        )

        # Loop continues - will go back to reviewer with revised draft

    # If we've exhausted all revision attempts, return what we have
    if verbose:
        print("\n[WARNING] Max revisions reached")

    return draft


# =============================================================================
# Even simpler: Sequential pipeline
# =============================================================================

def pipeline(*agents_and_prompts):
    """
    Run agents in sequence, passing each output to the next.

    This is an even simpler pattern - just a linear chain of agents.

    Args:
        *agents_and_prompts: Variable number of (agent, task) tuples

    Usage:
        result = pipeline(
            (RESEARCHER, "Research X"),
            (WRITER, "Write about the research"),
            (REVIEWER, "Review the content"),
        )

    Returns:
        The final agent's output
    """

    # Start with empty context
    context = ""

    # Loop through each (agent, task) pair
    for agent, task in agents_and_prompts:

        # Print progress
        print(f"\n[{agent.name}] {task[:50]}...")

        # Run the agent, passing previous output as context
        # The output becomes the context for the next agent
        context = run_single_agent(agent, task, context)

    # Return the final output
    return context


# =============================================================================
# Run it!
# =============================================================================

# Only run if this file is executed directly
if __name__ == "__main__":

    # Print header
    print("=" * 60)
    print("MULTI-AGENT DEMO - No Framework Required")
    print("=" * 60)

    # Run the full workflow with review loop
    result = research_and_write(
        "The benefits and challenges of remote work in 2024",
        verbose=True  # Print progress updates
    )

    # Print the final result
    print("\n" + "=" * 60)
    print("FINAL OUTPUT:")
    print("=" * 60)
    print(result)
