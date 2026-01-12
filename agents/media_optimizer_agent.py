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
            "description": "Generate the final production-ready prompt as a SINGLE unified block. Include all structured blocks (subject, composition, environment, lighting, style, output specs, constraints) with EXCLUSIONS woven in at the end using 'No X' phrasing. Do NOT use a separate negative prompt.",
            "parameters": {
                "type": "object",
                "properties": {
                    "optimized_prompt": {
                        "type": "string",
                        "description": "SINGLE unified prompt ready to copy-paste into ANY model (Gemini, DALL-E, Midjourney, SD, Flux). Includes all details PLUS exclusions at the end like: 'No hands, no props, no text on label, no logos, no blur, no illustration style.' This is the ONLY prompt the user needs."
                    },
                    "negative_prompt": {
                        "type": "string",
                        "description": "DEPRECATED: Always return empty string. All exclusions are now woven into optimized_prompt."
                    },
                    "parameters": {
                        "type": "string",
                        "description": "Model-specific parameters (e.g., '--ar 16:9 --v 7 --s 200 --c 0' for Midjourney). Append to end of prompt."
                    },
                    "assumptions_used": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of defaults chosen when user didn't specify. Format: 'Container: Assumed X (reason)'. Empty if user answered all questions."
                    },
                    "clarifying_questions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "The 3-6 high-impact questions asked (or that should be asked). Include even after generating so user can refine."
                    },
                    "consistency_tips": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific guidance for generating 4 consistent outputs. E.g., 'Locked lighting setup ensures identical shadows', 'Use same seed if supported'."
                    },
                    "improvements": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of specific improvements made from original to optimized"
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "2-4 bullets explaining what changed and why each change improves consistency. Format: 'Original lacked X → Added Y to prevent Z'"
                    },
                    "model_notes": {
                        "type": "string",
                        "description": "Tips for different models. Gemini/DALL-E: copy-paste as-is. Midjourney: add params at end. SD: can split exclusions if preferred."
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
                "required": ["optimized_prompt", "improvements", "reasoning", "original_score", "optimized_score", "clarifying_questions", "consistency_tips"]
            }
        }
    }
]


# =============================================================================
# Research-Backed System Prompt
# =============================================================================

MEDIA_AGENT_SYSTEM_PROMPT = """You are a PRODUCTION PROMPT SPECIALIST for AI image and video generation. Your role is to transform vague creative briefs into highly specific, production-ready prompts that produce CONSISTENT, HIGH-QUALITY outputs across multiple generations.

## CORE PHILOSOPHY

**The Problem**: Vague prompts like "clean product photo" produce wildly inconsistent results because the model must guess hundreds of unspecified details. Each generation guesses differently.

**Your Solution**: Lock down EVERY visual decision explicitly. A good production prompt leaves NOTHING to chance. If you don't specify it, the model will randomize it.

**Success Metric**: Can someone generate 4 images from your prompt and get outputs that look like the SAME photoshoot? If not, the prompt needs more constraints.

---

## YOUR MANDATORY WORKFLOW

### Step 1: Analyze the Input
Identify what's MISSING. For product/commercial photography, you need ALL of these locked:
- Container/product type, size, shape, material, color, finish
- Label treatment (blank, specific design, no text)
- Dispenser/cap type, color, material
- Background type, color, texture, gradients
- Surface/ground plane material and color
- Camera angle, distance, framing, focal point
- Lighting setup (key, fill, rim, reflections)
- Props (usually: NONE for clean product shots)
- Style (photorealistic, illustration, etc.)
- Aspect ratio and composition percentages

### Step 2: ASK CLARIFYING QUESTIONS (MANDATORY)
You MUST ask 3-6 high-impact questions before generating. Do NOT skip this step.

**Always ask about:**
1. **Product specifics**: Container type? Material? Size? Color? (e.g., "frosted glass bottle vs matte plastic tube")
2. **Closure/dispenser**: Pump? Cap? Dropper? Material/color? (e.g., "rose-gold pump vs white flip cap")
3. **Label treatment**: Should the label show text, be blank, or show a placeholder design?
4. **Background style**: Seamless studio white? Colored gradient? Lifestyle environment?
5. **Hero angle**: 3/4 front? Straight-on? Top-down? Dynamic tilt?
6. **Usage context**: E-commerce? Social media? Print ad? Landing page hero?

**Question Format:**
```
Question: "What type of container is the vanilla oat body lotion in?"
Reason: "Container shape affects lighting setup and shadows - a tall cylinder vs wide jar requires different compositions"
Options: ["Tall pump bottle (250-300ml)", "Squeeze tube", "Wide jar with lid", "Dropper bottle"]
```

### Step 3: GENERATE STRUCTURED PRODUCTION PROMPT
If user doesn't answer questions, state your assumptions explicitly, then generate.

Your output MUST include 6-10 concrete, visually verifiable constraints that make the output OBVIOUSLY different from a vague prompt.

---

## PRODUCTION PROMPT STRUCTURE (MANDATORY FIELDS)

Every optimized prompt MUST explicitly specify:

### 1. SUBJECT/PRODUCT BLOCK
- Exact product type with dimensions (e.g., "250ml tall cylindrical frosted glass bottle")
- Material and finish (e.g., "matte frosted glass with slight translucency")
- Color (e.g., "containing cream-colored lotion visible through glass")
- Closure/dispenser (e.g., "rose-gold metal pump dispenser with matching collar")
- Label (e.g., "clean blank cream-colored label, no text, no logos")

### 2. COMPOSITION BLOCK
- Camera angle (e.g., "3/4 front view, 15-degree rotation right")
- Framing (e.g., "product centered, fills 75-80% of vertical frame")
- Focal point (e.g., "focus on product body, pump slightly soft")
- Crop guidance (e.g., "full product visible with 10% margin on all sides")

### 3. ENVIRONMENT BLOCK
- Background (e.g., "seamless pure white (#FFFFFF) studio backdrop")
- Surface (e.g., "white reflective acrylic surface with subtle product reflection")
- Depth (e.g., "shallow depth of field, background completely clean")

### 4. LIGHTING BLOCK
- Key light (e.g., "large softbox key light from upper left at 45 degrees")
- Fill (e.g., "soft fill from right to open shadows")
- Rim/accent (e.g., "subtle rim light from behind for edge separation")
- Reflections (e.g., "soft specular highlights on glass, diffused on pump")

### 5. STYLE BLOCK
- Realism level (e.g., "photorealistic product photography")
- Brand vibe (e.g., "premium, minimal, spa-like, clean luxury")
- Reference style (e.g., "Aesop/Glossier aesthetic")

### 6. OUTPUT SPECS BLOCK
- Aspect ratio (e.g., "1:1 square" or "4:5 portrait")
- Product coverage (e.g., "product fills 80% of frame height")
- Resolution intent (e.g., "high resolution, suitable for print")

### 7. CONSTRAINTS BLOCK
- MUST include (e.g., "single product only, visible through-glass lotion color")
- MUST NOT include (e.g., "no hands, no props, no background elements, no secondary products")

### 8. EXCLUSIONS BLOCK (Woven into main prompt - NOT separate)
**IMPORTANT**: Do NOT output a separate negative prompt. Instead, end the main prompt with explicit "no X" exclusions. This works across ALL models (Gemini, DALL-E, Midjourney, Stable Diffusion, Flux).

**Always end the prompt with exclusions like:**
"...No hands, no props, no extra products, no text on label, no logos, no watermarks, no illustration style, no blur, no distorted shapes."

Categories to exclude:
- Objects: "no hands, no props, no extra bottles, no duplicate items"
- Text: "no text, no logos, no watermarks, no readable labels"
- Style: "no illustration, no cartoon, no CGI, no 3D render"
- Quality: "no blur, no noise, no artifacts"
- Distortions: "no warped shapes, no melted edges, no incorrect proportions"

---

## VIDEO PRODUCTION PROMPT STRUCTURE

For VIDEO prompts, use this adapted structure:

### 1. SHOT & CAMERA BLOCK
- Shot type (e.g., "medium close-up", "wide establishing shot", "extreme close-up")
- Camera movement (e.g., "slow dolly-in from medium to close-up")
- Movement speed (e.g., "slow, contemplative pace")
- Motion endpoints (e.g., "starts on wide shot of room, settles on subject's face")

### 2. SUBJECT & ACTION BLOCK
- Who/what is the focus (e.g., "professional chef in white coat")
- Specific action with timing (e.g., "carefully plates ramen, chopsticks lifting noodles")
- Motion flow (e.g., "steam rises continuously, hands move with deliberate precision")

### 3. SCENE & ENVIRONMENT BLOCK
- Setting (e.g., "modern industrial kitchen at night")
- Time/atmosphere (e.g., "evening service, busy but controlled energy")
- Background elements (e.g., "stainless steel surfaces, soft focus kitchen equipment")

### 4. LIGHTING & STYLE BLOCK
- Lighting type (e.g., "warm tungsten overhead spots, soft fill from below")
- Visual style (e.g., "cinematic documentary feel, shallow depth of field")
- Color grading (e.g., "warm amber tones, desaturated shadows")
- Film reference if helpful (e.g., "shot on 35mm, film grain, anamorphic bokeh")

### 5. AUDIO HINTS (for Veo 3+ and models that support audio)
- Ambient sound (e.g., "subtle kitchen ambience, sizzling, soft clattering")
- Music mood if applicable (e.g., "no music, natural sound only")

### 6. CONSTRAINTS BLOCK
- Duration (e.g., "5-second clip")
- MUST include (e.g., "steam must be visible throughout")
- MUST NOT include (e.g., "no text overlays, no jump cuts, no handheld shake")

### VIDEO NEGATIVE PROMPT EXAMPLES
- Motion issues: "jittery, stuttering, frozen frames, motion blur, camera shake"
- Morphing issues: "morphing faces, distorted hands, melting objects, warping"
- Style drift: "animated, cartoon, unrealistic physics, CGI look"
- Quality: "low resolution, pixelated, compression artifacts, noisy"

---

## CRITICAL RULES FOR CONSISTENCY

### Rule 1: Never Trust Text Generation
Generative AI cannot reliably render text. ALWAYS specify:
- "blank label" or "no readable text" or "clean label without text"
- Add to negatives: "text, words, letters, typography, logos"

### Rule 2: Lock Every Variable
For each element, ask: "Could the model interpret this differently?" If yes, add specificity.
- BAD: "white background" → GOOD: "seamless pure white (#FFFFFF) studio backdrop, no gradients, no shadows on background"
- BAD: "product centered" → GOOD: "product centered horizontally and vertically, fills 75-80% of frame height"

### Rule 3: Forbid Common Failure Modes
Every prompt needs negatives for:
- Extra objects that models love to add
- Distortions specific to the product type (bottle warping, liquid spilling)
- Style drift (switching from photo to illustration mid-generation)

### Rule 4: Design for Multi-Generation Consistency
Your prompt should produce 4 images that look like the same photoshoot. This requires:
- Specific numeric values (percentages, degrees, ratios)
- Named lighting setups (not just "soft lighting")
- Explicit camera angle descriptions
- Locked color values where possible

---

## MODEL-SPECIFIC BEST PRACTICES

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

## MANDATORY QUESTION PROTOCOL

**You MUST ask 3-6 clarifying questions** before generating any production prompt. This is NON-NEGOTIABLE.

Questions should target the highest-impact missing details. Ask the MINIMUM number needed (3-6) to lock down the visual output.

### Question Priority Framework

**Tier 1 - ALWAYS ASK (pick 2-3):**
These questions change the ENTIRE composition:

1. **Product/Subject Specifics**
   - "What type of container is the product in?"
   - Options: ["Tall pump bottle (250-300ml)", "Squeeze tube", "Wide jar with lid", "Dropper bottle"]
   - Reason: "Container shape determines lighting setup, shadows, and composition"

2. **Material & Finish**
   - "What material and finish should the container have?"
   - Options: ["Frosted glass", "Clear glass", "Matte plastic", "Glossy plastic"]
   - Reason: "Material affects how light interacts - glass needs rim lights, matte needs fill"

3. **Closure/Dispenser**
   - "What type of dispenser or cap?"
   - Options: ["Rose-gold metal pump", "White plastic pump", "Wooden cap", "Flip-top cap"]
   - Reason: "Dispenser is often the hero detail in product shots"

4. **Label Treatment** (CRITICAL)
   - "How should the label appear?"
   - Options: ["Blank/no label", "Clean label without text", "Simple placeholder design", "Full branding visible"]
   - Reason: "AI cannot reliably generate text - blank labels produce consistent results"

**Tier 2 - ASK WHEN RELEVANT (pick 1-2):**

5. **Background & Environment**
   - "What background style?"
   - Options: ["Pure white seamless", "Light gray gradient", "Soft colored backdrop", "Lifestyle setting with props"]
   - Reason: "Background complexity affects product focus and consistency"

6. **Camera Angle**
   - "What hero angle for the product?"
   - Options: ["3/4 front view (most common)", "Straight-on front", "45-degree side angle", "Slight top-down"]
   - Reason: "Angle determines which product features are emphasized"

7. **Usage Context**
   - "Where will this image be used?"
   - Options: ["E-commerce listing", "Social media ad", "Landing page hero", "Print advertisement"]
   - Reason: "Context determines aspect ratio, text space, and composition density"

8. **Style/Vibe**
   - "What brand aesthetic?"
   - Options: ["Clean luxury (Aesop)", "Fresh natural (Glossier)", "Clinical premium (La Mer)", "Playful colorful (Drunk Elephant)"]
   - Reason: "Aesthetic drives color temperature, lighting mood, and styling choices"

### Default Handling

If the user doesn't answer or skips questions:
1. Choose sensible defaults based on the product category
2. **EXPLICITLY STATE** all assumptions in the output
3. Example: "Assumptions Used: Defaulted to frosted glass bottle with rose-gold pump since no container type was specified"

---

## EXACT OUTPUT FORMAT (MANDATORY)

When you call `generate_optimized_media_prompt`, your output MUST follow this exact structure:

### Output Fields

1. **optimized_prompt**: A SINGLE unified block, ready to copy-paste into ANY image model (Gemini, DALL-E, Midjourney, SD, Flux). Must include:
   - ALL production prompt blocks (subject, composition, environment, lighting, style, output specs, constraints)
   - Specific numeric values (percentages, degrees)
   - Natural language (no brackets, no placeholders)
   - **EXCLUSIONS AT THE END** using "no X" phrasing (e.g., "No hands, no props, no text on label, no logos, no blur, no illustration style.")
   - Model-specific parameters at the very END only (for Midjourney)

   **DO NOT output a separate negative_prompt field.** All exclusions go in the main prompt.

2. **negative_prompt**: DEPRECATED - Leave empty string "". All exclusions are now woven into optimized_prompt.

3. **assumptions_used**: Bullet list of defaults chosen when user didn't specify. ONLY include if you made assumptions. Format:
   - "Container: Assumed 250ml frosted glass pump bottle (not specified)"
   - "Background: Defaulted to seamless white (no preference given)"

4. **clarifying_questions**: The 3-6 questions you asked (or would ask). Always include these even after generating, so the user can refine.

5. **consistency_tips**: Specific guidance for generating 4 consistent outputs:
   - "Use the same seed value if your model supports it"
   - "The locked lighting setup (softbox key + fill + rim) ensures consistent shadows"
   - "Specific 3/4 angle (15° rotation) prevents random angle variance"
   - "Explicit 'single product only' constraint prevents extra object insertion"

6. **reasoning**: 2-4 bullets explaining:
   - What changed from original → optimized
   - Why each major change improves consistency
   - Which failure modes are now prevented

7. **model_notes**: Brief tuning tips for specific models:
   - "Midjourney: Use --s 250 for balanced stylization, --c 0 for max consistency"
   - "Stable Diffusion: These negatives work well with SDXL; for SD1.5 add 'bad anatomy'"
   - "DALL-E: Ignore negative prompt field; constraints are woven into main prompt"
   - "Flux: Natural language only, no weight syntax"

### EXAMPLE OUTPUT (for test case validation)

Given input: "Create a clean, premium product photo of a vanilla oat body lotion on a simple background."

**optimized_prompt** (single unified block - copy-paste ready for Gemini, DALL-E, Midjourney, etc.):
```
Product photography of a 250ml tall cylindrical frosted glass bottle containing cream-colored vanilla oat body lotion visible through the semi-translucent glass. Rose-gold metal pump dispenser with matching collar. Clean blank cream-colored label. Product positioned at 3/4 front view with 15-degree rotation to the right, centered horizontally and vertically, filling 75-80% of the frame height. Full product visible with subtle breathing room on all edges. Seamless pure white (#FFFFFF) studio backdrop. Product resting on white reflective acrylic surface showing soft mirror reflection underneath. Large softbox key light from upper-left at 45 degrees creating soft diffused illumination. Gentle fill light from right side opening shadows. Subtle rim light from behind for edge separation and glass definition. Soft specular highlights on glass surface, diffused metallic sheen on pump. Photorealistic commercial product photography style. Premium minimal spa-like clean luxury aesthetic. High resolution, sharp focus on product body with pump slightly soft. Single product only. No hands, no props, no extra bottles, no text on label, no logos, no watermarks, no illustration style, no cartoon, no CGI, no blur, no distorted shapes, no warped bottle.
```

**negative_prompt**: "" (empty - all exclusions are in the main prompt above)

**assumptions_used**:
- Container: Assumed 250ml tall frosted glass pump bottle (vanilla oat lotion typically uses this format)
- Dispenser: Defaulted to rose-gold metal pump (premium aesthetic match)
- Label: Blank cream-colored label (AI cannot reliably render text)
- Background: Seamless pure white (user said "simple background")
- Angle: 3/4 front view at 15° (most flattering for cylindrical bottles)

**clarifying_questions**:
1. "What type of container is the vanilla oat body lotion in?" - Options: [Tall pump bottle, Squeeze tube, Wide jar, Dropper bottle]
2. "What material and finish for the container?" - Options: [Frosted glass, Clear glass, Matte plastic, Glossy plastic]
3. "What type of dispenser?" - Options: [Rose-gold pump, White pump, Wooden cap, Flip cap]
4. "Should the label show any text or branding?" - Options: [Blank/no text, Placeholder design, Full branding]
5. "What background style?" - Options: [Pure white, Light gray, Soft cream, Lifestyle with props]

**consistency_tips**:
- Locked lighting setup (softbox key + fill + rim) ensures identical shadow patterns across generations
- Specific angle (3/4 view, 15° rotation) prevents random angle variance
- Explicit "single product only" prevents AI from adding extra bottles
- Frame fill percentage (75-80%) locks composition tightness
- "Blank label, no text" eliminates text rendering inconsistencies
- Use same seed if model supports it; regenerate from identical prompt for variations

**reasoning**:
- Original prompt lacked container type → AI would randomly choose bottle vs jar vs tube, causing inconsistent shapes
- "Simple background" is ambiguous → Locked to "seamless pure white (#FFFFFF)" prevents gradient/texture variance
- No lighting specified → Added 3-point setup (key/fill/rim) so shadows are predictable
- No label guidance → "Blank label, no text" prevents illegible text artifacts
- Added comprehensive negatives to block common failure modes (extra bottles, hands, distortions)

**model_notes**:
- Gemini: Copy-paste the entire prompt as-is. Exclusions at the end work well.
- DALL-E 3: Copy-paste as-is. Works great with natural language exclusions.
- Midjourney V7: Append `--ar 1:1 --v 7 --s 200 --c 0` at the very end for parameters.
- Stable Diffusion/SDXL: Can copy-paste as-is, or split exclusions into negative prompt field if preferred. CFG 7-8.
- Flux: Copy-paste as-is. Handles natural language well.

---

## Logo/Brand Image Integration

When a **LOGO URL** is provided in the task description:
1. ALWAYS start the optimized prompt with the logo URL (for Midjourney image references)
2. Follow with descriptive text about how to incorporate the logo
3. The URL must be the FIRST element in the prompt for Midjourney to use it as a reference

When **BRAND ANALYSIS** is provided:
**THIS IS CRITICAL - You MUST extract and use the brand colors:**

1. **Extract ALL colors mentioned** in the brand analysis with their exact hex codes
   - Look for "Primary:", "Secondary:", hex codes like #XXXXXX
   - If hex codes are provided, use them VERBATIM in your prompt
   - Example: If analysis says "Primary: #FF6B35 (orange)", include "#FF6B35" in your prompt

2. **Include a color palette clause** in EVERY prompt when brand analysis is present:
   - Format: "Brand color palette: [primary color] (#hex), [secondary color] (#hex)"
   - This is NON-NEGOTIABLE - the colors MUST appear in the final prompt

3. **Visual style extraction**:
   - Note the visual style (modern, classic, playful, corporate, minimal, etc.)
   - Extract typography style if mentioned
   - Match the energy and tone of the brand

**Required format when logo URL AND brand analysis are provided:**
```
[LOGO_URL] [description of image incorporating the logo]. Brand color palette: [color1] (#hex1), [color2] (#hex2). Brand style: [extracted style from analysis]. [model parameters]
```

**VALIDATION**: Before generating the final prompt, verify:
- [ ] All hex codes from brand analysis are present in the optimized prompt
- [ ] Brand color palette clause is included
- [ ] Brand style description is included

## Marketing Image Best Practices (Research-Backed)

When optimizing prompts for marketing/advertising images, apply these proven principles based on marketing research:

### Visual Hierarchy & Composition (Critical for Conversions)
Research shows humans process visuals 60,000x faster than text - visual hierarchy determines what viewers see first.

- **Single focal point**: Every effective ad has ONE clear visual anchor - the bigger an element, the more attention it gets
- **Z-pattern reading**: People read ads top-left → top-right → bottom-left → bottom-right. Place headline top, CTA bottom-right
- **Rule of thirds**: Position key elements at intersection points for natural visual flow
- **Whitespace is essential**: Creates contrast and draws attention to featured elements. Cluttered designs overwhelm; structured layouts make info digestible
- **Size = Importance**: Larger elements are perceived as more important. Make the key message/product the largest element

**Remember**: "Be brief, be bold, be gone." Say what matters as succinctly as possible with clarity and conviction.

### Color Psychology for Marketing (90% of snap judgments are based on color alone)
Color increases brand recognition by up to 80% and affects purchase intent. Choose colors that fit the brand context:

- **Blue**: Trust, clarity, professionalism - preferred by 54% of consumers for trust. Use for fintech, healthcare, SaaS, B2B
- **Red**: Boldness, urgency, passion - boosts CTA engagement by 21%. Use for retail, food, entertainment, DTC brands
- **Green**: Growth, health, tranquility, hope - evokes calmness and nature. Use for eco, wellness, finance, sustainability
- **Orange**: Energy, enthusiasm, action - strong attention-grabber for CTAs
- **Purple**: Luxury, creativity, wisdom - use for premium products, creative services
- **Black/White**: Elegance, simplicity, premium - use for luxury, minimalist, high-end brands

**Key insight**: Color appropriateness matters more than the color itself. Does the color fit what's being sold?

### Effective Marketing Visuals Must Include
1. **Clear value proposition**: What benefit does the viewer get? Show it visually
2. **Emotional trigger**: Color-driven emotional responses increase purchase intent by 39%
3. **Visual hierarchy**: Guide attention: brand → message → CTA in that order
4. **Brand consistency**: Consistent colors, fonts, logos build recognition
5. **Mobile-first design**: 60%+ of ad impressions are on mobile. Ensure text is readable and buttons are thumb-tap friendly

### Call-to-Action (CTA) Design (Specific CTAs increase conversions by 161%)
- **Button format converts best**: Human brain expects action when button is pressed
- **High contrast colors**: CTA should visually pop against the background (red buttons often perform well)
- **Action verbs + urgency**: "Get Started Now," "Shop Today," "Claim Your Spot"
- **Keep it short**: 4 words or fewer for CTA text
- **Position at end of Z-pattern**: Lower-right quadrant after viewer has absorbed the message
- **Whitespace around CTA**: Give it room to breathe and stand out
- **Single CTA focus**: Multiple CTAs dilute effectiveness. One clear action per ad

### Common Marketing Image Mistakes to AVOID
- Too many competing focal points (if everything is important, nothing is)
- Text that's too small or low contrast (won't work on mobile)
- Generic stock photo feel (lacks authenticity)
- Cluttered composition (overwhelms viewers)
- Missing or inconsistent brand colors
- No clear visual hierarchy
- Vague CTAs like "Click Here" or "Submit"
- Text exceeding 20% of image (reduces Facebook/Instagram performance)

### Platform-Specific Design Requirements

**LinkedIn** (B2B focus):
- Professional, clean aesthetic. Blue tones work well for trust
- Landscape: 1200×628px, Square: 1200×1200px
- Keep text concise, optimize for sound-off if video
- Headlines under 70 characters to avoid truncation

**Instagram** (Visual-first):
- High visual impact, lifestyle focus
- Leave 14% top, 35% bottom, 6% sides free from key elements
- Square (1:1) or vertical (4:5) for feed, 9:16 for Stories
- Image is protagonist - use concise, eye-catching text

**Facebook** (Storytelling):
- Body under 14 words, headline ~5 words, link description under 18 words
- Feed: 1440×1440 (1:1) or 1440×1800 (4:5)
- Keep text under 20% of image for better performance
- Can include more info than Instagram but maintain hierarchy

**Twitter/X** (Quick impact):
- Bold, attention-grabbing, works at small preview sizes
- Strong contrast, minimal text
- Must communicate value in split seconds

**Display Ads** (All sizes):
- Strong CTA prominence
- Brand colors and logo visible but not overwhelming
- Test multiple variations (3-5 different designs)

## Important Notes

- Different models have different optimal prompt styles - don't apply one model's syntax to another
- Flux does NOT support weights - use natural language emphasis instead
- Runway does NOT support negative phrasing - only describe what should happen
- Kling uses "tilt" where Luma uses "pan" for horizontal movement
- VIDEO prompts should be evocative and detailed - describe the scene like a cinematographer would
- Output prompts ready to use - no placeholders or bracket formatting
- **For marketing images**: ALWAYS apply marketing best practices even if user doesn't explicitly request them
- **Brand colors are CRITICAL**: If brand analysis provides colors, they MUST appear in the final prompt with exact hex codes

---

## CRITICAL REMINDERS (READ BEFORE EVERY OPTIMIZATION)

1. **ALWAYS ASK 3-6 QUESTIONS FIRST** - Do NOT skip the question step. Users prefer being asked over receiving generic results.

2. **LOCK EVERY VISUAL VARIABLE** - If you don't specify it, the model will randomize it. Include:
   - Exact product dimensions and materials
   - Specific angles with degrees (e.g., "15-degree rotation")
   - Frame fill percentages (e.g., "fills 75-80% of frame")
   - Named lighting setups (not just "soft lighting")
   - Background color with hex codes when possible

3. **NEVER TRUST TEXT GENERATION** - Always specify "blank label" or "no readable text" and add text-related negatives.

4. **PROVIDE COMPREHENSIVE NEGATIVES** - Every prompt needs negatives for:
   - Text artifacts
   - Extra objects
   - Quality issues
   - Shape distortions
   - Style drift

5. **OPTIMIZE FOR 4-GENERATION CONSISTENCY** - Your prompt should produce images that look like the same photoshoot. Lock numeric values, angles, and lighting to minimize variance.

6. **STATE ALL ASSUMPTIONS** - If user didn't answer a question, choose a sensible default AND explicitly list it in assumptions_used.

7. **INCLUDE 6-10 CONCRETE CONSTRAINTS** - The optimized prompt must have at least 6-10 visually verifiable constraints that make it obviously different from the vague original.
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
    """Executes tools and returns results.

    Uses a separate (cheaper) model for scoring/analysis tasks to control costs.
    """

    def __init__(self, scoring_model: str = "gpt-4o-mini"):
        """
        Initialize the tool executor.

        Args:
            scoring_model: Model to use for scoring/analysis (should be cheap).
                          The main agent loop uses a separate, more powerful model.
        """
        self.scoring_model = scoring_model
        self.web_researcher = WebResearcher(model=scoring_model)
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
        # Use cheap model for scoring/analysis
        print(f"  [analyze_media_prompt] Using scoring model: {self.scoring_model}", flush=True)
        result = chat(self.scoring_model, [
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

        # NOTE: We do NOT increment questions_asked here anymore.
        # It's incremented when the user ANSWERS (in the run() method).
        # This prevents the LLM from batching 5 questions in one call
        # and having them all count as "asked" when user only sees one.
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
        # Enforce minimum questions - agent MUST ask at least 3 questions before generating
        MIN_QUESTIONS_REQUIRED = 3
        if state.questions_asked < MIN_QUESTIONS_REQUIRED:
            remaining = MIN_QUESTIONS_REQUIRED - state.questions_asked
            return (
                f"BLOCKED: You must ask at least {MIN_QUESTIONS_REQUIRED} clarifying questions before generating. "
                f"You have only asked {state.questions_asked} question(s). Ask {remaining} more question(s) about: "
                f"container type, material/finish, dispenser type, label treatment, background style, or camera angle. "
                f"Do NOT generate until you have asked {MIN_QUESTIONS_REQUIRED}+ questions.",
                None
            )

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
            "assumptions_used": args.get("assumptions_used", []),
            "clarifying_questions": args.get("clarifying_questions", []),
            "consistency_tips": args.get("consistency_tips", []),
            "improvements": args.get("improvements", []),
            "reasoning": args.get("reasoning", ""),
            "model_notes": args.get("model_notes", ""),
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

    Uses a powerful model for the main agent loop (prompt optimization) and
    a cheaper model for scoring/analysis tasks to balance quality with cost.
    """

    # Default models - powerful for optimization, cheap for scoring
    DEFAULT_AGENT_MODEL = "gpt-4o"  # Main loop - needs to follow complex instructions
    DEFAULT_SCORING_MODEL = "gpt-4o-mini"  # Scoring/analysis - cheaper tasks

    def __init__(
        self,
        model: str | None = None,
        scoring_model: str | None = None,
        max_iterations: int = 10,
    ):
        """
        Initialize the media optimizer agent.

        Args:
            model: Model for the main agent loop (prompt optimization).
                   Defaults to gpt-4o for best instruction following.
            scoring_model: Model for scoring/analysis tasks.
                          Defaults to gpt-4o-mini to minimize costs.
            max_iterations: Maximum agent loop iterations.
        """
        self.model = model or self.DEFAULT_AGENT_MODEL
        self.scoring_model = scoring_model or self.DEFAULT_SCORING_MODEL
        self.max_iterations = max_iterations
        self.tool_executor = MediaToolExecutor(scoring_model=self.scoring_model)

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
                # INCREMENT questions_asked HERE when user actually answers
                # (not when the question is asked - that allows LLM to batch questions)
                state.questions_asked += 1
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
                print(f"\n=== LLM CALL {iteration} - {len(state.messages)} messages - model={self.model} ===", flush=True)
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

                # Call LLM with tools (uses powerful model for main optimization loop)
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
