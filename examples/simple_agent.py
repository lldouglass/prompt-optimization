"""
Simple AI Agent - No Framework Required

This demonstrates that an "agent" is just:
1. An LLM with a system prompt
2. Tools it can call
3. A loop that runs until done

No LangGraph, CrewAI, or AutoGen needed.
"""

# json module lets us parse the tool arguments that come back as JSON strings
import json

# os module lets us read environment variables (for the API key)
import os

# OpenAI is the official Python client for calling GPT models
from openai import OpenAI

# Create an OpenAI client instance using the API key from environment variables
# This client will be used to make all our API calls to GPT
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


# =============================================================================
# STEP 1: Define your tools (functions the agent can call)
# =============================================================================

# This is a regular Python function that simulates searching the web
# In a real app, you'd call Google, Bing, or a search API here
def search_web(query: str) -> str:
    """Simulate a web search."""

    # Fake database of search results (in production, call a real API)
    fake_results = {
        "python": "Python is a programming language created by Guido van Rossum in 1991.",
        "javascript": "JavaScript is a scripting language for web browsers, created in 1995.",
        "rust": "Rust is a systems programming language focused on safety, created by Mozilla.",
    }

    # Loop through our fake results to find a match
    for key, value in fake_results.items():
        # Check if the search query contains any of our keywords
        if key in query.lower():
            # Return the matching result
            return value

    # If no match found, return a "no results" message
    return f"No results found for: {query}"


# This function evaluates math expressions
def calculate(expression: str) -> str:
    """Evaluate a math expression."""

    # try/except catches errors if the expression is invalid
    try:
        # eval() executes a string as Python code
        # WARNING: eval is dangerous in production - use a safe math parser instead
        result = eval(expression)

        # Return the result as a formatted string
        return f"Result: {result}"

    except Exception as e:
        # If there's an error (bad expression), return the error message
        return f"Error: {e}"


# This function returns the current time
def get_current_time() -> str:
    """Get the current time."""

    # Import datetime module to get current time
    from datetime import datetime

    # Get current time and format it as a readable string
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# This dictionary maps function names (strings) to actual Python functions
# When the LLM says "call search_web", we look up "search_web" in this dict
# and get the actual function to execute
TOOLS = {
    "search_web": search_web,      # "search_web" -> search_web function
    "calculate": calculate,         # "calculate" -> calculate function
    "get_current_time": get_current_time,  # "get_current_time" -> get_current_time function
}

# These are the tool definitions in OpenAI's required format
# The LLM reads these to understand what tools are available and how to call them
# This is like an API specification for each function
TOOL_DEFINITIONS = [
    {
        # Type is always "function" for callable tools
        "type": "function",

        # The function definition with name, description, and parameters
        "function": {

            # Name must match a key in our TOOLS dictionary above
            "name": "search_web",

            # Description tells the LLM when to use this tool
            "description": "Search the web for information about a topic",

            # Parameters define what arguments the function accepts
            # This uses JSON Schema format
            "parameters": {
                "type": "object",  # Parameters are passed as an object/dict

                # Define each parameter
                "properties": {
                    "query": {
                        "type": "string",  # The query parameter is a string
                        "description": "The search query"  # Helps LLM understand what to pass
                    }
                },

                # List of required parameters (query is required)
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a mathematical expression",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The math expression to evaluate, e.g. '2 + 2 * 3'"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current date and time",

            # This function takes no parameters
            "parameters": {
                "type": "object",
                "properties": {}  # Empty - no parameters needed
            }
        }
    }
]


# =============================================================================
# STEP 2: The agent loop (this is the entire "framework")
# =============================================================================

def run_agent(task: str, max_iterations: int = 10, verbose: bool = True) -> str:
    """
    Run an agent to complete a task.

    Args:
        task: The task/question for the agent to handle
        max_iterations: Maximum number of loop iterations (prevents infinite loops)
        verbose: If True, print debug information

    Returns:
        The agent's final answer as a string
    """

    # The system prompt defines WHO the agent is and HOW it should behave
    # This is the most important part - it shapes all the agent's responses
    system_prompt = """You are a helpful research assistant.

Your job is to help users by:
1. Searching for information when needed
2. Performing calculations when asked
3. Providing clear, accurate answers

IMPORTANT:
- Use tools when you need external information
- Think step by step
- When you have enough information, provide your final answer
- Be concise but thorough"""

    # Initialize the conversation history
    # This is a list of message dictionaries that grows as the conversation progresses
    messages = [
        # First message is always the system prompt (sets agent behavior)
        {"role": "system", "content": system_prompt},

        # Second message is the user's task/question
        {"role": "user", "content": task}
    ]

    # Counter to track how many times we've gone through the loop
    iteration = 0

    # THE MAIN AGENT LOOP
    # This keeps running until either:
    # 1. The agent gives a final answer (no more tool calls)
    # 2. We hit max_iterations (safety limit)
    while iteration < max_iterations:

        # Increment the iteration counter
        iteration += 1

        # Print debug info if verbose mode is on
        if verbose:
            print(f"\n--- Iteration {iteration} ---")

        # =================================================================
        # CALL THE LLM
        # This is where we send the conversation to GPT and get a response
        # =================================================================
        response = client.chat.completions.create(
            # Which model to use (gpt-4o-mini is fast and cheap)
            model="gpt-4o-mini",

            # The full conversation history (system + user + any previous messages)
            messages=messages,

            # Tell the model what tools are available
            tools=TOOL_DEFINITIONS,

            # "auto" means the model decides whether to use tools or respond directly
            # Other options: "none" (never use tools), "required" (must use a tool)
            tool_choice="auto"
        )

        # Extract the assistant's message from the response
        # response.choices is a list (usually just one choice)
        # .message contains the actual content
        message = response.choices[0].message

        # finish_reason tells us why the model stopped generating
        # "stop" = normal completion (gave an answer)
        # "tool_calls" = wants to call a tool
        finish_reason = response.choices[0].finish_reason

        # Add the assistant's response to our conversation history
        # This is important - the model needs to see its own previous responses
        messages.append(message)

        # =================================================================
        # CHECK IF THE MODEL WANTS TO CALL TOOLS
        # =================================================================
        if message.tool_calls:
            # The model wants to use one or more tools

            if verbose:
                print(f"Agent wants to call {len(message.tool_calls)} tool(s)")

            # Loop through each tool call the model wants to make
            # (It can request multiple tool calls in one response)
            for tool_call in message.tool_calls:

                # Get the name of the function to call (e.g., "search_web")
                function_name = tool_call.function.name

                # Parse the arguments from JSON string to Python dict
                # e.g., '{"query": "python"}' becomes {"query": "python"}
                arguments = json.loads(tool_call.function.arguments)

                if verbose:
                    print(f"  Calling: {function_name}({arguments})")

                # ==========================================================
                # EXECUTE THE TOOL
                # ==========================================================
                if function_name in TOOLS:
                    # Look up the function in our TOOLS dictionary
                    # Then call it with the arguments using ** to unpack the dict
                    # e.g., TOOLS["search_web"](**{"query": "python"})
                    # becomes: search_web(query="python")
                    result = TOOLS[function_name](**arguments)
                else:
                    # If the model hallucinates a tool that doesn't exist
                    result = f"Error: Unknown tool '{function_name}'"

                if verbose:
                    print(f"  Result: {result}")

                # ==========================================================
                # ADD TOOL RESULT TO CONVERSATION
                # ==========================================================
                # We tell the model what the tool returned
                # This goes back into the conversation so the model can use it
                messages.append({
                    # Role "tool" indicates this is a tool response
                    "role": "tool",

                    # tool_call_id links this result to the specific tool call
                    # (important when there are multiple tool calls)
                    "tool_call_id": tool_call.id,

                    # The actual result from running the tool
                    "content": result
                })

            # After processing all tool calls, the loop continues
            # The model will see the tool results and decide what to do next

        # =================================================================
        # CHECK IF THE MODEL IS DONE
        # =================================================================
        elif finish_reason == "stop":
            # The model gave a final answer (no tool calls)

            if verbose:
                print("Agent finished!")

            # Return the model's final response
            # message.content is the text of the response
            return message.content

    # If we get here, we've hit max_iterations without completing
    # This is a safety fallback to prevent infinite loops
    return "Max iterations reached without completion"


# =============================================================================
# STEP 3: Run it!
# =============================================================================

# This block only runs if you execute this file directly
# (not when importing it as a module)
if __name__ == "__main__":

    # Define some example tasks to test the agent
    tasks = [
        "What is Python and when was it created?",
        "What is 15% of 847?",
        "Search for information about Rust, then tell me when it was created and calculate how many years old it is.",
    ]

    # Print a header
    print("=" * 60)
    print("SIMPLE AGENT DEMO - No Framework Required")
    print("=" * 60)

    # Loop through each task and run the agent on it
    for i, task in enumerate(tasks, 1):  # enumerate with start=1 for 1-based numbering

        # Print task header
        print(f"\n{'='*60}")
        print(f"TASK {i}: {task}")
        print("=" * 60)

        # Run the agent and get the result
        result = run_agent(task, verbose=True)

        # Print the final answer
        print(f"\n>>> FINAL ANSWER:\n{result}")
