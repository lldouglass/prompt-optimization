// Demo configuration for landing page
// Update these values when swapping demo images

export const beforeImages: string[] = [
  // Add your "before" image filenames here (ideally 4)
  // Example: "before-1.png", "before-2.png", etc.
  // Images should be placed in public/demo/before/
]

export const afterImages: string[] = [
  // Add your "after" image filenames here (ideally 4)
  // Example: "after-1.png", "after-2.png", etc.
  // Images should be placed in public/demo/after/
]

export const originalPrompt =
  "Create a clean, premium product photo for a vanilla oat body lotion on a simple background."

export const optimizedPrompt = `Product photography of a 250ml tall cylindrical frosted glass bottle containing cream-colored vanilla oat body lotion visible through the semi-translucent glass. Rose-gold metal pump dispenser with matching collar. Clean blank cream-colored label with no text, no logos, no readable elements. Product positioned at 3/4 front view with 15-degree rotation to the right, centered horizontally and vertically, filling 75-80% of the frame height. Full product visible with subtle breathing room on all edges. Seamless pure white (#FFFFFF) studio backdrop with no gradients, no shadows on background. Product resting on white reflective acrylic surface showing soft mirror reflection underneath. Large softbox key light from upper-left at 45 degrees creating soft diffused illumination. Gentle fill light from right side opening shadows. Subtle rim light from behind for edge separation and glass definition. Soft specular highlights on glass surface, diffused metallic sheen on pump. Photorealistic commercial product photography style. Premium minimal spa-like clean luxury aesthetic. High resolution, sharp focus on product body with pump slightly soft. Single product only, no hands, no props, no secondary items, no background elements.`

// These are the actual questions the Clayrnt agent asks (minimum 3, typically 5)
export const clarifyingQuestions: string[] = [
  "What type of container is the vanilla oat body lotion in?",
  "What material and finish should the container have?",
  "What type of dispenser or cap?",
  "How should the label appear?",
  "What background style?",
]

export const checklist: { label: string; met: boolean }[] = [
  { label: "Frosted glass bottle", met: true },
  { label: "Rose-gold pump", met: true },
  { label: "Blank label, no readable text", met: true },
  { label: "Clean seamless background", met: true },
  { label: "Centered hero framing", met: true },
  { label: "Soft studio lighting, subtle shadow", met: true },
  { label: "No props", met: true },
  { label: "No hands", met: true },
  { label: "No extra products", met: true },
  { label: "No text artifacts", met: false },
]

export const matchScore = "9/10"

// Product brief shown in the demo
export const productBrief = {
  product: "Vanilla Oat Body Lotion",
  mustHaves: [
    "frosted glass bottle",
    "rose-gold pump",
    "blank label (no readable text)",
    "clean studio background",
    "no props",
  ],
}
