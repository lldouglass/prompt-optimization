/**
 * TypeScript types for Video Workflow feature.
 * Matches Pydantic schemas from backend.
 */

// ============================================================================
// Enums
// ============================================================================

export type WorkflowGoal =
  | "product_ad"
  | "ugc"
  | "explainer"
  | "cinematic_brand"
  | "tutorial"
  | "other"

export type WorkflowPlatform =
  | "tiktok"
  | "instagram"
  | "youtube"
  | "web"
  | "other"

export type AspectRatio = "9:16" | "1:1" | "16:9"

export type WorkflowStatus = "draft" | "in_progress" | "completed"

export type ShotType = "wide" | "medium" | "close" | "detail"

export type CameraMove =
  | "none"
  | "pan"
  | "tilt"
  | "orbit"
  | "push_in"
  | "pull_out"
  | "crane"

export type QuestionCategory =
  | "shot_style"
  | "pacing"
  | "camera_movement"
  | "action_beats"
  | "audio"
  | "cta"

export type ExportFormat = "json" | "markdown"

// ============================================================================
// Brief Intake (Steps 1-2)
// ============================================================================

export interface ClarifyingQuestion {
  id: string
  question: string
  category: QuestionCategory
  answer?: string
}

export interface BriefIntake {
  project_name: string
  goal: WorkflowGoal
  platform: WorkflowPlatform
  aspect_ratio: AspectRatio
  duration_seconds: number
  brand_vibe: string[]
  avoid_vibe: string[]
  must_include: string[]
  must_avoid: string[]
  script_or_vo?: string
  product_or_subject_description: string
  reference_images?: string[]
}

export interface BriefData extends BriefIntake {
  clarifying_questions: ClarifyingQuestion[]
}

// ============================================================================
// Continuity Pack (Step 3)
// ============================================================================

export interface Anchor {
  type: string
  description: string
}

export interface LightingRecipe {
  key_light: string
  fill_light: string
  rim_light?: string
  softness: string
  time_of_day: string
}

export interface PaletteAnchor {
  name: string
  hex: string
}

export interface ContinuityPack {
  anchors: Anchor[]
  lighting_recipe?: LightingRecipe
  palette_anchors: PaletteAnchor[]
  do_list: string[]
  dont_list: string[]
  style_clause?: string
}

// ============================================================================
// Shot Plan (Step 4)
// ============================================================================

export interface Shot {
  id: string
  shot_number: number
  start_sec: number
  end_sec: number
  shot_type: ShotType
  camera_move: CameraMove
  framing_notes: string
  subject_action_beats: string[]
  setting_notes: string
  audio_cue?: string
  purpose: string
}

export interface ShotPlan {
  shots: Shot[]
}

// ============================================================================
// Prompt Pack (Step 5)
// ============================================================================

export interface SoraParams {
  resolution: string
  duration: number
  aspect_ratio: string
  fps: number
  seed?: number
}

export interface ShotPrompt {
  shot_id: string
  sora_params: SoraParams
  prompt_text: string
  negative_prompt_text?: string
  dialogue_block?: string
}

export interface PromptPack {
  target_model: string
  prompts: ShotPrompt[]
}

// ============================================================================
// QA Score (Step 6)
// ============================================================================

export interface QAFix {
  issue: string
  fix: string
}

export interface QAScore {
  ambiguity_risk: number
  motion_complexity_risk: number
  continuity_completeness: number
  audio_readiness: number
  overall_score: number
  warnings: string[]
  fixes: QAFix[]
  recommended_questions: string[]
}

// ============================================================================
// Versions (Step 7)
// ============================================================================

export interface VersionSnapshot {
  version_number: number
  step: "brief" | "continuity" | "shots" | "prompts"
  data: Record<string, unknown>
  created_at: string
}

// ============================================================================
// Workflow
// ============================================================================

export interface VideoWorkflow {
  id: string
  name: string
  current_step: number
  status: WorkflowStatus
  is_template: boolean
  template_name?: string
  shot_count: number
  prompt_count: number
  overall_score?: number
  created_by?: string
  created_at: string
  updated_at: string
}

export interface VideoWorkflowDetail extends VideoWorkflow {
  source_template_id?: string
  brief?: BriefData
  continuity_pack?: ContinuityPack
  shot_plan?: ShotPlan
  prompt_pack?: PromptPack
  qa_score?: QAScore
  versions: VersionSnapshot[]
}

// ============================================================================
// API Request/Response Types
// ============================================================================

export interface CreateVideoWorkflowRequest {
  name: string
}

export interface AnswerQuestionsRequest {
  answers: Record<string, string>
}

export interface UpdateContinuityRequest {
  anchors?: Anchor[]
  lighting_recipe?: LightingRecipe
  palette_anchors?: PaletteAnchor[]
  do_list?: string[]
  dont_list?: string[]
  style_clause?: string
}

export interface UpdateShotRequest {
  shot_type?: ShotType
  camera_move?: CameraMove
  framing_notes?: string
  subject_action_beats?: string[]
  setting_notes?: string
  audio_cue?: string
  purpose?: string
  start_sec?: number
  end_sec?: number
}

export interface UpdatePromptRequest {
  prompt_text?: string
  negative_prompt_text?: string
  dialogue_block?: string
  sora_params?: SoraParams
}

export interface GeneratePromptsRequest {
  target_model?: string
}

export interface SaveVersionRequest {
  step: "brief" | "continuity" | "shots" | "prompts"
}

export interface CreateTemplateRequest {
  template_name: string
}

export interface CreateFromTemplateRequest {
  name: string
}

export interface ExportWorkflowResponse {
  format: ExportFormat
  filename: string
  content: string
}

// ============================================================================
// Step Configuration
// ============================================================================

export const WORKFLOW_STEPS = [
  { number: 1, name: "Brief Intake", key: "brief" },
  { number: 2, name: "Clarifying Questions", key: "questions" },
  { number: 3, name: "Continuity Pack", key: "continuity" },
  { number: 4, name: "Shot Plan", key: "shots" },
  { number: 5, name: "Prompt Pack", key: "prompts" },
  { number: 6, name: "QA Score", key: "qa" },
  { number: 7, name: "Export", key: "export" },
] as const

export const GOAL_OPTIONS: { value: WorkflowGoal; label: string }[] = [
  { value: "product_ad", label: "Product Ad" },
  { value: "ugc", label: "UGC / User Generated" },
  { value: "explainer", label: "Explainer Video" },
  { value: "cinematic_brand", label: "Cinematic Brand Film" },
  { value: "tutorial", label: "Tutorial / How-To" },
  { value: "other", label: "Other" },
]

export const PLATFORM_OPTIONS: { value: WorkflowPlatform; label: string }[] = [
  { value: "tiktok", label: "TikTok" },
  { value: "instagram", label: "Instagram Reels" },
  { value: "youtube", label: "YouTube" },
  { value: "web", label: "Website / Web" },
  { value: "other", label: "Other" },
]

export const ASPECT_RATIO_OPTIONS: { value: AspectRatio; label: string }[] = [
  { value: "9:16", label: "9:16 Portrait" },
  { value: "1:1", label: "1:1 Square" },
  { value: "16:9", label: "16:9 Landscape" },
]

export const DURATION_OPTIONS = [6, 12, 15, 30, 60] as const

export const SHOT_TYPE_OPTIONS: { value: ShotType; label: string }[] = [
  { value: "wide", label: "Wide" },
  { value: "medium", label: "Medium" },
  { value: "close", label: "Close-Up" },
  { value: "detail", label: "Detail / Insert" },
]

export const CAMERA_MOVE_OPTIONS: { value: CameraMove; label: string }[] = [
  { value: "none", label: "Static / Locked" },
  { value: "pan", label: "Pan" },
  { value: "tilt", label: "Tilt" },
  { value: "orbit", label: "Orbit" },
  { value: "push_in", label: "Push In / Dolly In" },
  { value: "pull_out", label: "Pull Out / Dolly Out" },
  { value: "crane", label: "Crane / Jib" },
]
