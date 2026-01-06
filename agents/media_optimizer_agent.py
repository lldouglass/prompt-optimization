"""
Agent-based Media Prompt Optimizer

Uses an LLM agent loop with tools to optimize prompts for AI image and video generation.
Supports: Midjourney, Stable Diffusion, DALL-E, Flux (photo) and Runway, Luma, Kling, Veo (video).

The agent decides:
- Whether to analyze the prompt against model-specific best practices
- Whether to search the web for examples
- Whether to ask the user clarifying questions
- When to generate the final optimized prompt with correct syntax
"""

import json
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Literal

from llm.client import chat_with_tools, create_tool_result_message, ChatWithToolsResponse
from agents.web_researcher import WebResearcher


# =============================================================================
# Tool Definitions (OpenAI format)
# =============================================================================

MEDIA_OPTIMIZER_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "analyze_media_prompt",
            "description": "Analyze the media prompt against best practices for the target model. Call this first to understand what needs improvement.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt_text": {
                        "type": "string",
                        "description": "The prompt text to analyze"
                    },
                    "media_type": {
                        "type": "string",
                        "enum": ["photo", "video"],
                        "description": "Whether this is for image or video generation"
                    },
                    "target_model": {
                        "type": "string",
                        "enum": ["midjourney", "stable_diffusion", "dalle", "flux", "runway", "luma", "kling", "veo", "generic"],
                        "description": "The AI model this prompt will be used with"
                    }
                },
                "required": ["prompt_text", "media_type", "target_model"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for prompt examples and techniques for the specific model. Use when you need style references or model-specific syntax examples.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for finding relevant examples (e.g., 'midjourney portrait lighting prompts')"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ask_user_question",
            "description": "Ask the user a multiple-choice question to gather preferences. Always provide 2-4 helpful options. The user can also type a custom answer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question to ask the user"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Brief explanation of why this question helps optimization"
                    },
                    "options": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "2-4 suggested answer options for the user to choose from. User can also type a custom answer.",
                        "minItems": 2,
                        "maxItems": 4
                    }
                },
                "required": ["question", "reason", "options"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_optimized_media_prompt",
            "description": "Generate the final optimized prompt with model-specific syntax. Include parameters for Midjourney, weights for Stable Diffusion, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "optimized_prompt": {
                        "type": "string",
                        "description": "The optimized prompt text with model-specific syntax"
                    },
                    "negative_prompt": {
                        "type": "string",
                        "description": "Negative prompt for Stable Diffusion (leave empty for other models)"
                    },
                    "parameters": {
                        "type": "string",
                        "description": "Additional parameters (e.g., '--ar 16:9 --v 7' for Midjourney)"
                    },
                    "improvements": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of specific improvements made"
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Brief explanation of why these changes improve the prompt"
                    },
                    "original_score": {
                        "type": "number",
                        "description": "Estimated score of the original prompt (0-10)"
                    },
                    "optimized_score": {
                        "type": "number",
                        "description": "Estimated score of the optimized prompt (0-10)"
                    },
                    "tips": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Model-specific tips for getting better results"
                    }
                },
                "required": ["optimized_prompt", "improvements", "reasoning", "original_score", "optimized_score"]
            }
        }
    }
]


# =============================================================================
# Research-Backed System Prompt
# =============================================================================

MEDIA_AGENT_SYSTEM_PROMPT = """You are a media prompt optimization specialist. Your role is to improve prompts for AI image and video generation based on researched best practices for each specific model.

## Your Approach

1. Analyze the user's prompt and target model
2. Identify missing elements based on model-specific best practices
3. Ask clarifying questions only when critical information is ambiguous
4. Generate an optimized prompt using the correct syntax and structure for the target model

## Model-Specific Best Practices

### MIDJOURNEY V7

**Key Insight**: V7 works best with simpler, more natural language. Avoid over-engineering.

**Best Practices**:
- Use compound subjects: "a family picnic" instead of listing each person
- Front-load the most important subject/concept
- Anchor all important details - unspecified elements are filled by the model
- Parameters go at the END: --ar 16:9 --v 7 --s 500

**Parameters**:
- `--ar` Aspect ratio (16:9, 9:16, 1:1, 4:3, 21:9)
- `--s` Stylize (0-1000): higher = more artistic, less prompt adherence
- `--c` Chaos (0-100): higher = more variation
- `--no` Exclude elements (e.g., --no text)
- `--v 7` Version

**Avoid**: Over-complex prompts with excessive keywords, negative phrasing in prompt text, relying on text rendering

---

### STABLE DIFFUSION / SDXL

**Key Insight**: Keyword-based with optional weights, plus separate negative prompt.

**Best Practices**:
- Front-load important keywords (position affects weight)
- Use weights sparingly: (keyword:1.2) = +20% emphasis. Stay under 1.4
- SDXL needs fewer negative prompts than SD 1.5
- Quality boosters when appropriate: masterpiece, best quality, highly detailed
- 75 token limit for SD v1 - be concise

**Syntax**:
- `(keyword:1.2)` - increase weight by 20%
- `(keyword:0.8)` - decrease weight by 20%
- Negative prompt: separate field for exclusions

**Negative Prompt Guidelines**: Only include specific things to avoid. Common: bad anatomy, blurry, low quality, watermark, extra limbs

**Avoid**: Weights above 1.4, overly long prompts, putting negative terms in main prompt

---

### DALL-E 3

**Key Insight**: Natural, conversational language. Shorter often works better.

**Best Practices**:
- Describe like you're telling a story to someone
- Be specific about setting, objects, colors, mood
- Pick one main style (don't mix cartoon + photorealistic)
- Use spatial words for layout: "on the left," "in the foreground"
- Focus on what you WANT, not what to avoid

**Avoid**: Technical jargon, negative prompting (counterproductive), overly long prompts, multiple conflicting styles

---

### FLUX

**Key Insight**: Natural language with NO weight syntax. Front-load important elements.

**Best Practices**:
- Use "with emphasis on" or "focus on" to highlight elements
- Front-load the most important details (model weights earlier tokens more)
- Always specify artistic style (defaults to realistic if omitted)
- Be specific and detailed - Flux thrives on information

**Avoid**: SD-style weight syntax like (keyword:1.2) - it doesn't work, "white background" in [dev] variant causes issues, leaving style unspecified

---

### RUNWAY GEN-4

**Key Insight**: Clear physical actions with rich visual context. No negative phrasing.

**Structure**: Subject movement → Camera motion → Visual context/atmosphere/style

**Best Practices**:
- Translate concepts into clear, executable physical actions
- Use evocative verbs with context: "slowly turns toward camera, steam rising around them"
- Specify movement in spatial context: "walks through the doorway into golden afternoon light"
- Include atmosphere: lighting, color palette, mood, environment details
- Design prompts that leave room for camera movement: "wide shot with space on left for pan"
- Add cinematic references when helpful: "shot on 35mm, shallow depth of field"
- Duration: 5s for simple actions, 10s for complex sequences
- Camera speed: Low = clean edges, Medium = cinematic, High = artifacts risk

**Camera Movements**: Tracking, Panning, Tilt, Dolly, Handheld

**Avoid**: Negative phrasing like "don't" or "without" (not supported), over-describing when using input images, multiple simultaneous camera transforms

---

### LUMA DREAM MACHINE

**Key Insight**: Natural, richly detailed language works best. Be descriptive and evocative.

**Best Practices**:
- Describe like a conversation - paint a vivid picture with words
- Include sensory details: lighting, textures, atmosphere, colors
- Be specific about camera motion: "camera smoothly pans right, revealing a sunset beach with golden light reflecting off gentle waves"
- Match camera movement energy to subject energy
- Works best for realistic content over animated
- Film terminology helps: "Film still," "Captured by ARRI Alexa," "anamorphic lens flare"
- Describe the mood and feeling, not just the action

**Features**: @character for consistency, @style for visual reference, type "camera" for motion controls

**Avoid**: Overly technical jargon, animated/cartoon requests (not its strength)

---

### KLING AI

**Key Insight**: Structured prompts with motivated camera movement and rich scene details.

**Structure**: Subject → Action → Context/Atmosphere (+ camera modifiers)

**Best Practices**:
- Camera movement must serve the story - be motivated
- Tell camera WHAT to focus on: "camera slowly zooms in on her eyes, catching the reflection of candlelight"
- Include environment and atmosphere: lighting, weather, time of day, textures
- Use "static shot" or "fixed lens" when you want no camera movement
- Speed modifiers with context: "slowly reveals," "dramatically pulls back to show"
- Describe the emotional tone: "intimate," "dramatic," "serene"

**Important**: Use "tilt left" for horizontal movement (NOT "pan left" - that's Luma terminology)

**Camera Commands**: Zoom in, Pullback, Rotate around, Tilt up/down, 360 rotation

**Avoid**: Multiple simultaneous camera transforms (causes warping), unmotivated movement, confusing pan/tilt terminology

---

### VEO (Google)

**Key Insight**: More detail = more control. Shot type and rich descriptions are critical.

**Structure**: Shot type + Subject + Context/Atmosphere + Action

**Best Practices**:
- Always specify shot type (wide shot, medium shot, close-up, extreme close-up)
- Lead with format declaration: realistic, animated, stop-motion
- Include rich environmental details: "rain-slicked streets reflecting neon signs"
- Map out exact play-by-play for action sequences with timing
- Describe lighting and color: "golden hour light," "cool blue shadows"
- Veo 3+: Define sounds explicitly in separate sentences
- Add texture and material descriptions: "weathered wood," "gleaming chrome"

**Style Options**: "ultra-realistic rendering", "shot on 35mm film", "Japanese anime style", "stop-motion animation", "cinematic color grading"

**Avoid**: Leaving shot type unspecified (model guesses), vague action descriptions, missing atmosphere details

---

## Available Tools

1. **analyze_media_prompt**: Score the prompt and identify model-specific issues. Call this first.
2. **search_web**: Find examples for specific models/styles when needed.
3. **ask_user_question**: Ask multiple-choice questions to gather user preferences. Always provide 2-4 helpful options.
4. **generate_optimized_media_prompt**: Output the final optimized prompt.

## When to Ask Questions

**Ask questions proactively** to create better prompts. Users prefer being asked than receiving a generic optimization. Always provide 2-4 multiple-choice options that represent common preferences.

**STRATEGIC QUESTIONS (ask 1-2 of these first - they create the biggest impact):**

These questions produce structurally different outputs, not just polished versions:

1. **Primary objective**: "What is the ONE thing this image must make the viewer do or understand?"
   - Options: ["Take action (click, buy, sign up)", "Feel an emotion (trust, excitement, curiosity)", "Understand a concept quickly", "Remember the brand"]
   - Reason: "This becomes the core constraint that shapes the entire composition"

2. **Differentiation**: "What should this image clearly communicate that competitors usually don't?"
   - Options: ["Speed/efficiency", "Human touch/authenticity", "Technical sophistication", "Simplicity/ease of use"]
   - Reason: "This ensures the image stands out rather than looking generic"

3. **Avoidance**: "What should this image explicitly avoid?"
   - Options: ["Stock photo feel", "Text-heavy design", "Generic corporate imagery", "Overly complex visuals"]
   - Reason: "Knowing what NOT to do is as important as knowing what to do"

**Good questions to ask (pick 1-2 relevant ones):**

For ALL prompts:
- **Style/mood**: "What visual style are you going for?" Options: Photorealistic, Cinematic, Artistic/Painterly, Stylized/Graphic
- **Aspect ratio**: "What aspect ratio do you need?" Options vary by model (16:9, 9:16, 1:1, etc.)
- **Color palette**: "What color mood fits your vision?" Options: Warm tones, Cool tones, High contrast, Muted/Pastel

For PHOTO prompts:
- **Lighting**: "What lighting style?" Options: Natural daylight, Golden hour, Studio lighting, Dramatic/moody
- **Composition**: "What framing?" Options: Close-up portrait, Medium shot, Wide establishing shot, Detail/macro

For VIDEO prompts:
- **Camera movement**: "What camera movement?" Options: Static shot, Slow pan, Tracking shot, Dynamic/handheld
- **Pacing**: "What's the energy level?" Options: Slow and contemplative, Medium/natural, Fast and dynamic
- **Duration focus**: "What's most important?" Options: Single clear action, Atmospheric mood, Character moment

**Example good question:**
```
Question: "What visual style are you going for?"
Reason: "This helps me apply the right artistic modifiers for Midjourney"
Options: ["Photorealistic", "Cinematic film look", "Digital art/illustration", "Painterly/artistic"]
```

## Output Format

When generating the optimized prompt:

### CRITICAL: Prompt Construction with User Constraints

If the user answered any strategic questions, you MUST inject their answers as explicit constraint clauses at the START of the optimized prompt. Use the user's exact words - do not paraphrase.

**Required structure when strategic answers are provided:**

```
[Base prompt description]

This image must primarily communicate: [user's answer to primary objective question]

Visually emphasize: [user's answer to differentiation question]

Avoid the following visual or messaging elements: [user's answer to avoidance question]

Ensure the primary message is readable within the first 2 seconds on mobile.
```

**Rules:**
- If user left an answer blank or didn't answer a strategic question, OMIT that clause entirely
- Inject user answers VERBATIM as constraints - do not paraphrase or interpret
- The constraint clauses go AFTER the main visual description but BEFORE model-specific parameters
- Always include the mobile readability hint for marketing/advertisement images

**Example final prompt:**
```
Create a digital LinkedIn advertisement showing a modern dashboard interface with real-time analytics.

This image must primarily communicate: automated prompt testing and iteration saves time.

Visually emphasize: before-and-after prompt comparison with visible quality scores.

Avoid the following visual or messaging elements: stock SaaS photos, generic productivity buzzwords, decorative-only gradients.

Ensure the primary message is readable within the first 2 seconds on mobile.

Clean, modern layout with subtle depth and professional color palette. --ar 1:1 --v 7
```

### Logo/Brand Image Integration

When a **LOGO URL** is provided in the task description:
1. ALWAYS start the optimized prompt with the logo URL (for Midjourney image references)
2. Follow with descriptive text about how to incorporate the logo
3. The URL must be the FIRST element in the prompt for Midjourney to use it as a reference

When **BRAND ANALYSIS** is provided:
1. Extract dominant colors (include hex codes if visible, e.g., "#2563eb")
2. Note the visual style (modern, classic, playful, corporate, minimal, etc.)
3. Include a "Brand style:" constraint in the prompt with these extracted elements
4. Match the energy and tone of the brand

**Required format when logo URL is provided:**
```
[LOGO_URL] [description of image incorporating the logo], Brand style: [extracted style from analysis]. [model parameters]
```

**Example with logo:**
```
https://res.cloudinary.com/xxx/logo.png a professional LinkedIn advertisement featuring this logo prominently in the top-left corner, showing a modern dashboard interface with analytics charts, Brand style: modern tech aesthetic with navy blue (#2563eb), clean sans-serif typography, generous whitespace, subtle depth through shadows. --ar 1:1 --v 7
```

### Output Fields

1. **optimized_prompt**: Ready to paste into the AI tool. Use correct model syntax.
   - For VIDEO prompts: Be RICH and DESCRIPTIVE. Include atmosphere, lighting, colors, textures, mood, and cinematic details. Video prompts should paint a vivid picture - aim for 2-4 detailed sentences.
   - For PHOTO prompts: Follow model-specific length guidelines (natural for DALL-E, keyword-rich for SD).
   - ALWAYS include strategic constraint clauses if user provided answers

2. **negative_prompt**: Only for Stable Diffusion. Leave empty for other models.

3. **parameters**: Only for Midjourney. Format: --ar 16:9 --v 7 --s 500. Leave empty for other models.

4. **improvements**: List specific changes made based on best practices:
   - "Front-loaded subject description for better model interpretation"
   - "Added atmospheric details: lighting, mood, and environment"
   - "Included cinematic camera movement with spatial context"
   - "Applied SDXL weight syntax to emphasize key elements"
   - "Injected user's primary objective as explicit constraint"
   - "Added differentiation clause based on user input"
   - "Included explicit avoidance constraints"

5. **reasoning**: Explain how changes align with the model's documented best practices.

6. **tips**: 2-3 actionable tips specific to this model.

## Important Notes

- Different models have different optimal prompt styles - don't apply one model's syntax to another
- Flux does NOT support weights - use natural language emphasis instead
- Runway does NOT support negative phrasing - only describe what should happen
- Kling uses "tilt" where Luma uses "pan" for horizontal movement
- VIDEO prompts should be evocative and detailed - describe the scene like a cinematographer would
- Output prompts ready to use - no placeholders or bracket formatting
"""


# =============================================================================
# WebSocket Message Types
# =============================================================================

@dataclass
class WebSocketMessage:
    """Base class for WebSocket messages."""
    type: str
    data: dict = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps({"type": self.type, **self.data})


def msg_tool_called(tool_name: str, args: dict, result_summary: str = "") -> dict:
    """Create a tool_called message."""
    return {
        "type": "tool_called",
        "tool": tool_name,
        "args": args,
        "result_summary": result_summary[:200] if result_summary else "",
    }


def msg_question(question_id: str, question: str, reason: str, options: list[str] | None = None) -> dict:
    """Create a question message for user input with multiple choice options."""
    return {
        "type": "question",
        "question_id": question_id,
        "question": question,
        "reason": reason,
        "options": options or [],
    }


def msg_progress(step: str, message: str) -> dict:
    """Create a progress update message."""
    return {
        "type": "progress",
        "step": step,
        "message": message,
    }


def msg_completed(result: dict) -> dict:
    """Create a completed message with final result."""
    return {
        "type": "completed",
        "result": result,
    }


def msg_error(error: str) -> dict:
    """Create an error message."""
    return {
        "type": "error",
        "error": error,
    }


# =============================================================================
# Agent State
# =============================================================================

@dataclass
class MediaAgentState:
    """Mutable state for the media optimizer agent."""
    messages: list[dict] = field(default_factory=list)
    tool_calls_made: list[dict] = field(default_factory=list)
    questions_asked: int = 0
    max_questions: int = 5  # Allows 3 strategic + 2 style/technical questions
    web_sources: list[dict] = field(default_factory=list)
    analysis_result: Optional[dict] = None
    final_result: Optional[dict] = None
    error: Optional[str] = None
    status: Literal["running", "awaiting_input", "completed", "failed"] = "running"
    pending_question: Optional[dict] = None  # Current question awaiting answer
    strategic_answers: dict = field(default_factory=dict)  # Store strategic question answers


# =============================================================================
# Tool Implementations
# =============================================================================

class MediaToolExecutor:
    """Executes tools and returns results."""

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.web_researcher = WebResearcher(model=model)
        self.original_prompt = ""
        self.media_type = "photo"
        self.target_model = "generic"

    async def execute(
        self,
        tool_name: str,
        args: dict,
        state: MediaAgentState,
    ) -> tuple[str, Optional[dict]]:
        """
        Execute a tool and return the result.

        Returns:
            Tuple of (result_string, optional_special_action)
            special_action can be {"pause": question_data} or {"complete": result_data}
        """
        if tool_name == "analyze_media_prompt":
            return await self._analyze_media_prompt(args, state)
        elif tool_name == "search_web":
            return await self._search_web(args, state)
        elif tool_name == "ask_user_question":
            return self._ask_user_question(args, state)
        elif tool_name == "generate_optimized_media_prompt":
            return self._generate_optimized(args, state)
        else:
            return f"Unknown tool: {tool_name}", None

    async def _analyze_media_prompt(self, args: dict, state: MediaAgentState) -> tuple[str, None]:
        """Analyze a media prompt against model-specific best practices."""
        prompt_text = args.get("prompt_text", "")
        media_type = args.get("media_type", "photo")
        target_model = args.get("target_model", "generic")

        # Store for later use
        self.media_type = media_type
        self.target_model = target_model

        # Model-specific scoring criteria
        model_criteria = self._get_model_criteria(target_model, media_type)

        analysis_prompt = f"""Analyze this {media_type} prompt for {target_model}:

---
{prompt_text}
---

{model_criteria}

Return a JSON object with:
{{
  "score": <0-10>,
  "issues": [
    {{"category": "subject|style|syntax|structure|model_specific", "description": "...", "severity": "high|medium|low"}}
  ],
  "strengths": ["..."],
  "model_fit": "good|fair|poor",
  "priority_improvements": ["list of top improvements"],
  "missing_elements": ["what's missing for this model"],
  "syntax_issues": ["any model-specific syntax problems"],
  "ambiguities": ["list any critical ambiguities that need user clarification"]
}}"""

        from llm.client import chat
        result = chat(self.model, [
            {"role": "system", "content": "You are a media prompt analysis expert. Return only valid JSON."},
            {"role": "user", "content": analysis_prompt}
        ])

        # Parse the JSON result for structured storage
        try:
            parsed = json.loads(result)
            state.analysis_result = parsed
        except json.JSONDecodeError:
            state.analysis_result = {
                "raw": result,
                "issues": [],
                "strengths": [],
                "model_fit": "unknown",
                "priority_improvements": [],
                "missing_elements": [],
                "syntax_issues": [],
                "ambiguities": []
            }

        return result, None

    def _get_model_criteria(self, target_model: str, media_type: str) -> str:
        """Get model-specific scoring criteria."""
        if media_type == "video":
            return """
VIDEO PROMPT CRITERIA:
- Does it specify camera movement and shot type?
- Are motion endpoints defined (where movement starts and ends)?
- Does it use positive phrasing (no "don't" or "avoid")?
- Is the action/motion clearly described?
- Does it include lighting and atmosphere?
- Is it appropriate length (not too long for video models)?
"""

        # Photo models
        criteria = {
            "midjourney": """
MIDJOURNEY CRITERIA:
- Does it follow Subject → Medium → Environment → Lighting → Color → Mood structure?
- Are parameters at the end (--ar, --v, --s, --c)?
- Does it avoid negative phrasing in the main prompt?
- Are important elements placed first?
- Is stylize value appropriate for the desired effect?
""",
            "stable_diffusion": """
STABLE DIFFUSION CRITERIA:
- Does it use weighted tokens correctly? (word:1.2)
- Would it benefit from quality boosters (masterpiece, best quality)?
- Are important keywords front-loaded?
- Is it under 75 tokens?
- Would a negative prompt help?
""",
            "dalle": """
DALL-E 3 CRITERIA:
- Does it use natural, conversational language?
- Is it concise (shorter prompts work better)?
- Does it avoid technical jargon and parameters?
- Is it descriptive but not overly complex?
""",
            "flux": """
FLUX CRITERIA:
- Does it use weight syntax correctly? (word++, word--)
- Does it focus on positive descriptions?
- Is the description clean and direct?
""",
        }

        return criteria.get(target_model, """
GENERAL CRITERIA:
- Clear subject description
- Appropriate style terms
- Good structure and flow
- No contradictory elements
""")

    async def _search_web(self, args: dict, state: MediaAgentState) -> tuple[str, None]:
        """Search the web for examples."""
        query = args.get("query", "")

        if not self.web_researcher.is_available:
            return "Web search is not available (TAVILY_API_KEY not configured). Proceed without examples.", None

        try:
            result = await self.web_researcher.search(query, max_results=3)
            sources = []
            for r in result.get("results", []):
                sources.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "snippet": r.get("content", "")[:500],
                })
            state.web_sources.extend(sources)

            return json.dumps({
                "sources": sources,
                "note": "Use these examples to inform your optimization if relevant."
            }), None

        except Exception as e:
            return f"Web search failed: {str(e)}. Proceed without examples.", None

    def _ask_user_question(self, args: dict, state: MediaAgentState) -> tuple[str, dict]:
        """Ask user a multiple-choice question - pauses the agent."""
        question = args.get("question", "")
        reason = args.get("reason", "")
        options = args.get("options", [])

        if state.questions_asked >= state.max_questions:
            return f"Cannot ask more questions (max {state.max_questions} reached). Proceed with current information.", None

        state.questions_asked += 1
        state.status = "awaiting_input"
        state.pending_question = {
            "question": question,
            "reason": reason,
            "options": options,
        }

        # Return special action to pause
        return "Waiting for user response...", {"pause": state.pending_question}

    def _generate_optimized(self, args: dict, state: MediaAgentState) -> tuple[str, dict]:
        """Generate the final optimized prompt - completes the agent."""
        # Ensure analysis has the expected structure for the frontend
        analysis = state.analysis_result
        if analysis and isinstance(analysis, dict):
            # Ensure all expected fields exist
            if "issues" not in analysis:
                analysis["issues"] = []
            if "strengths" not in analysis:
                analysis["strengths"] = []
            if "model_fit" not in analysis:
                analysis["model_fit"] = "unknown"
            if "priority_improvements" not in analysis:
                analysis["priority_improvements"] = []

        result = {
            "original_prompt": self.original_prompt,
            "optimized_prompt": args.get("optimized_prompt", ""),
            "negative_prompt": args.get("negative_prompt", ""),
            "parameters": args.get("parameters", ""),
            "improvements": args.get("improvements", []),
            "reasoning": args.get("reasoning", ""),
            "original_score": args.get("original_score", 5.0),
            "optimized_score": args.get("optimized_score", 7.0),
            "tips": args.get("tips", []),
            "web_sources": state.web_sources,
            "analysis": analysis,
            "media_type": self.media_type,
            "target_model": self.target_model,
        }

        state.final_result = result
        state.status = "completed"

        return "Optimization complete.", {"complete": result}


# =============================================================================
# Media Optimizer Agent
# =============================================================================

class MediaOptimizerAgent:
    """
    Agent-based media prompt optimizer.

    Runs an LLM loop that decides which tools to use for optimization.
    Communicates progress via a callback function (for WebSocket updates).
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        max_iterations: int = 10,
    ):
        self.model = model
        self.max_iterations = max_iterations
        self.tool_executor = MediaToolExecutor(model=model)

    async def run(
        self,
        prompt: str,
        task_description: str,
        media_type: Literal["photo", "video"],
        target_model: str,
        on_message: Callable[[dict], Any],
        initial_state: Optional[MediaAgentState] = None,
        user_answer: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
    ) -> MediaAgentState:
        """
        Run the media optimizer agent.

        Args:
            prompt: The prompt to optimize (or description if generating from scratch)
            task_description: What they want to create
            media_type: "photo" or "video"
            target_model: Which AI model (midjourney, stable_diffusion, etc.)
            on_message: Callback for WebSocket messages (async or sync)
            initial_state: Optional state to resume from
            user_answer: Optional answer to pending question (for resume)
            aspect_ratio: Optional aspect ratio preference

        Returns:
            Final MediaAgentState with result or pending question
        """
        # Store original prompt for use in result
        self.tool_executor.original_prompt = prompt
        self.tool_executor.media_type = media_type
        self.tool_executor.target_model = target_model

        # Initialize or resume state
        if initial_state:
            state = initial_state
            if user_answer and state.pending_question:
                # The tool result for ask_user_question was already added when we paused.
                # Now add the user's answer as a user message so the agent can continue.
                state.messages.append({
                    "role": "user",
                    "content": f"User's answer to your question: {user_answer}"
                })
                state.pending_question = None
                state.status = "running"
        else:
            state = MediaAgentState()

            # Build aspect ratio guidance
            aspect_guidance = ""
            if aspect_ratio:
                aspect_guidance = f"\nDesired aspect ratio: {aspect_ratio}"

            # Build initial messages
            state.messages = [
                {"role": "system", "content": MEDIA_AGENT_SYSTEM_PROMPT},
                {"role": "user", "content": f"""Optimize this {media_type} prompt for {target_model}:

Task/Description: {task_description}

Current Prompt:
---
{prompt}
---
{aspect_guidance}

Start by analyzing the prompt against {target_model} best practices, ask clarifying questions if needed, then generate the optimized version with correct model-specific syntax."""}
            ]

        await self._send(on_message, msg_progress("starting", f"Beginning {media_type} optimization for {target_model}..."))

        iteration = 0
        while iteration < self.max_iterations and state.status == "running":
            iteration += 1

            try:
                # DEBUG: Print messages being sent to LLM
                print(f"\n=== LLM CALL {iteration} - {len(state.messages)} messages ===", flush=True)
                for i, msg in enumerate(state.messages):
                    role = msg.get("role", "?")
                    tool_calls = msg.get("tool_calls", [])
                    tool_call_id = msg.get("tool_call_id", "")
                    content_preview = str(msg.get("content", ""))[:50]
                    if tool_calls:
                        tc_ids = [tc.get("id", "?") for tc in tool_calls]
                        print(f"  [{i}] {role} tool_calls={tc_ids}", flush=True)
                    elif tool_call_id:
                        print(f"  [{i}] {role} tool_call_id={tool_call_id}", flush=True)
                    else:
                        print(f"  [{i}] {role}: {content_preview}...", flush=True)

                # Call LLM with tools
                response = chat_with_tools(
                    model=self.model,
                    messages=state.messages,
                    tools=MEDIA_OPTIMIZER_TOOLS,
                )

                # Add assistant message to history
                state.messages.append(response.to_message_dict())

                if response.has_tool_calls:
                    # Process ALL tool calls first, collecting results
                    # This ensures all tool results are added before any pause/complete
                    tool_results = []
                    pause_action = None
                    complete_action = None

                    for tool_call in response.tool_calls:
                        await self._send(on_message, msg_progress(
                            "tool",
                            f"Using {tool_call.name}..."
                        ))

                        # Execute the tool
                        result, action = await self.tool_executor.execute(
                            tool_call.name,
                            tool_call.arguments,
                            state,
                        )

                        # Log the tool call
                        state.tool_calls_made.append({
                            "tool": tool_call.name,
                            "args": tool_call.arguments,
                            "result_summary": result[:200] if result else "",
                        })

                        # Send tool update
                        await self._send(on_message, msg_tool_called(
                            tool_call.name,
                            tool_call.arguments,
                            result[:200] if result else ""
                        ))

                        # Collect tool result
                        tool_results.append((tool_call.id, result))

                        # Track special actions (but don't return yet)
                        if action:
                            if "pause" in action:
                                pause_action = (tool_call.id, action["pause"])
                            elif "complete" in action:
                                complete_action = action["complete"]

                    # Add ALL tool results to conversation history
                    # This is critical - OpenAI requires all tool_call_ids to have responses
                    for tool_call_id, result in tool_results:
                        state.messages.append(create_tool_result_message(
                            tool_call_id,
                            result
                        ))

                    # Now handle any pause/complete actions
                    if pause_action:
                        question_id, question_data = pause_action
                        await self._send(on_message, msg_question(
                            question_id,
                            question_data["question"],
                            question_data["reason"],
                            question_data.get("options", []),
                        ))
                        return state  # Return to wait for answer

                    if complete_action:
                        await self._send(on_message, msg_completed(complete_action))
                        return state

                elif response.finish_reason == "stop":
                    # Agent finished without calling generate_optimized_media_prompt
                    # Try to extract result from message content
                    if response.content:
                        state.final_result = {
                            "original_prompt": self.tool_executor.original_prompt,
                            "optimized_prompt": response.content,
                            "negative_prompt": "",
                            "parameters": "",
                            "improvements": ["Agent provided direct response"],
                            "reasoning": "No structured output provided",
                            "original_score": 5.0,
                            "optimized_score": 6.0,
                            "tips": [],
                            "web_sources": state.web_sources,
                            "media_type": media_type,
                            "target_model": target_model,
                        }
                        state.status = "completed"
                        await self._send(on_message, msg_completed(state.final_result))
                        return state

            except Exception as e:
                state.error = str(e)
                state.status = "failed"
                await self._send(on_message, msg_error(str(e)))
                return state

        # Max iterations reached
        if state.status == "running":
            state.status = "failed"
            state.error = "Max iterations reached without completion"
            await self._send(on_message, msg_error(state.error))

        return state

    async def _send(self, on_message: Callable, msg: dict):
        """Send a message via the callback."""
        import asyncio
        if asyncio.iscoroutinefunction(on_message):
            await on_message(msg)
        else:
            on_message(msg)
