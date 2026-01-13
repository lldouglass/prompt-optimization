const API_BASE = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api/v1`
  : "/api/v1"  // Use relative URL to go through Vite proxy in dev

// Timeout constants (in milliseconds)
const TIMEOUTS = {
  DEFAULT: 30000,      // 30s for normal requests
  OPTIMIZE: 120000,    // 2min for optimization (can be slow)
  AUTH: 15000,         // 15s for auth operations
  LONG: 60000,         // 60s for analysis/evaluation
}

// Fetch wrapper with timeout support using AbortController
async function fetchWithTimeout(
  url: string,
  options: RequestInit,
  timeoutMs: number = TIMEOUTS.DEFAULT
): Promise<Response> {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs)

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    })
    clearTimeout(timeoutId)
    return response
  } catch (error) {
    clearTimeout(timeoutId)
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error('Request timed out. Please check your connection and try again.')
    }
    throw error
  }
}

// Auth Types
export interface User {
  id: string
  email: string
  name: string | null
  avatar_url: string | null
  email_verified: boolean
  created_at: string
}

export interface OrganizationBasic {
  id: string
  name: string
  subscription_plan: string
}

export interface Membership {
  organization: OrganizationBasic
  role: string
}

export interface AuthResponse {
  user: User
  memberships: Membership[]
  current_organization: OrganizationBasic | null
}

// Types
export interface Organization {
  id: string
  name: string
  created_at: string
}

export interface ApiKey {
  id: string
  key_prefix: string
  name: string | null
  created_at: string
  last_used_at: string | null
  key?: string // Only present on creation
}

export interface LoggedRequest {
  id: string
  model: string
  provider: string
  messages: Array<{ role: string; content: string }>
  parameters: Record<string, unknown> | null
  response_content: string | null
  latency_ms: number | null
  input_tokens: number | null
  output_tokens: number | null
  cost_usd: number | null
  prompt_id: string | null
  tags: Record<string, unknown> | null
  trace_id: string | null
  created_at: string
  // Evaluation fields
  evaluation_score: number | null
  evaluation_subscores: Record<string, number> | null
  evaluation_tags: string[] | null
  evaluation_rationale: string | null
  evaluated_at: string | null
}

// Admin API (no auth required)
export const adminApi = {
  async createOrganization(name: string): Promise<Organization> {
    const res = await fetch(`${API_BASE}/admin/organizations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    })
    if (!res.ok) throw new Error("Failed to create organization")
    return res.json()
  },

  async listOrganizations(): Promise<Organization[]> {
    const res = await fetch(`${API_BASE}/admin/organizations`)
    if (!res.ok) throw new Error("Failed to list organizations")
    return res.json()
  },

  async createApiKey(orgId: string, name?: string): Promise<ApiKey> {
    const res = await fetch(`${API_BASE}/admin/organizations/${orgId}/api-keys`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    })
    if (!res.ok) throw new Error("Failed to create API key")
    return res.json()
  },

  async listApiKeys(orgId: string): Promise<ApiKey[]> {
    const res = await fetch(`${API_BASE}/admin/organizations/${orgId}/api-keys`)
    if (!res.ok) throw new Error("Failed to list API keys")
    return res.json()
  },

  async deleteApiKey(keyId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/admin/api-keys/${keyId}`, {
      method: "DELETE",
    })
    if (!res.ok) throw new Error("Failed to delete API key")
  },
}

// Authenticated API
export function createAuthenticatedApi(apiKey: string) {
  const headers = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${apiKey}`,
  }

  return {
    async listRequests(params?: { limit?: number; offset?: number; trace_id?: string }): Promise<LoggedRequest[]> {
      const searchParams = new URLSearchParams()
      if (params?.limit) searchParams.set("limit", String(params.limit))
      if (params?.offset) searchParams.set("offset", String(params.offset))
      if (params?.trace_id) searchParams.set("trace_id", params.trace_id)

      const res = await fetch(`${API_BASE}/requests?${searchParams}`, { headers })
      if (!res.ok) throw new Error("Failed to list requests")
      return res.json()
    },

    async getRequest(id: string): Promise<LoggedRequest> {
      const res = await fetch(`${API_BASE}/requests/${id}`, { headers })
      if (!res.ok) throw new Error("Failed to get request")
      return res.json()
    },

    async evaluateRequest(id: string): Promise<LoggedRequest> {
      const res = await fetch(`${API_BASE}/requests/${id}/evaluate`, {
        method: "POST",
        headers,
      })
      if (!res.ok) throw new Error("Failed to evaluate request")
      return res.json()
    },

    // Billing endpoints
    async getBillingInfo(): Promise<BillingInfo> {
      const res = await fetch(`${API_BASE}/billing`, { headers })
      if (!res.ok) throw new Error("Failed to get billing info")
      return res.json()
    },

    async createCheckoutSession(plan: string, billingPeriod: "monthly" | "yearly" = "monthly"): Promise<CheckoutSessionResponse> {
      const res = await fetch(`${API_BASE}/billing/checkout`, {
        method: "POST",
        headers,
        body: JSON.stringify({ plan, billing_period: billingPeriod }),
      })
      if (!res.ok) throw new Error("Failed to create checkout session")
      return res.json()
    },

    async createPortalSession(): Promise<PortalSessionResponse> {
      const res = await fetch(`${API_BASE}/billing/portal`, {
        method: "POST",
        headers,
      })
      if (!res.ok) throw new Error("Failed to create portal session")
      return res.json()
    },
  }
}

// Agent types
export interface Skill {
  name: string
  description: string
  tags: string[]
  model: string
  max_tokens: number
  temperature: number
}

export interface PlanStep {
  skill: string
  input_mapping: Record<string, string>
  notes: string
}

export interface Plan {
  reasoning: string
  steps: PlanStep[]
  is_valid: boolean
  errors: string[]
}

export interface ExecuteResult {
  content: string
  model: string
  usage: Record<string, number>
  skill: string
}

export interface ClaimVerification {
  claim: string
  status: "verified" | "contradicted" | "unverified"
  evidence: string
  source: string | null
}

export interface HallucinationReport {
  has_hallucinations: boolean
  verified_claims: ClaimVerification[]
  contradicted_claims: ClaimVerification[]
  unverified_claims: ClaimVerification[]
  summary: string
}

export interface Judgment {
  scores: Record<string, number>
  overall_score: number
  passed: boolean
  strengths: string[]
  weaknesses: string[]
  reasoning: string
  hallucination_check: HallucinationReport | null
}

export interface CompareResult {
  winner: string
  confidence: string
  comparison: Record<string, { winner: string; explanation: string }>
  reasoning: string
  hallucination_check_a: HallucinationReport | null
  hallucination_check_b: HallucinationReport | null
}

// Optimization types
export interface AnalysisIssue {
  category: string
  description: string
  severity: string
}

export interface PromptAnalysis {
  issues: AnalysisIssue[]
  strengths: string[]
  overall_quality: string
  priority_improvements: string[]
}

export interface FewShotExample {
  input: string
  output: string
  rationale: string
}

export interface FewShotResearch {
  examples: FewShotExample[]
  format_recommendation: string
  research_notes: string
}

export interface OptimizationResult {
  original_prompt: string
  optimized_prompt: string
  original_score: number
  optimized_score: number
  improvements: string[]
  reasoning: string
  analysis: PromptAnalysis | null
  few_shot_research: FewShotResearch | null
  file_context: FileProcessingResult[] | null
}

// Agent-based optimization types (WebSocket)
export interface AgentSessionResponse {
  session_id: string
  status: "running" | "awaiting_input" | "completed" | "failed"
  message: string | null
}

export interface PendingQuestion {
  question_id: string
  question: string
  reason: string
  options?: string[]
}

export interface ToolCallInfo {
  tool: string
  args: Record<string, unknown>
  result_summary: string
}

export type AgentWebSocketMessage =
  | { type: "progress"; step: string; message: string }
  | { type: "tool_called"; tool: string; args: Record<string, unknown>; result_summary: string }
  | { type: "question"; question_id: string; question: string; reason: string; options?: string[] }
  | { type: "completed"; result: OptimizationResult }
  | { type: "error"; error: string }

// WebSocket message type for media agent (returns MediaAgentResult)
export type MediaAgentWebSocketMessage =
  | { type: "progress"; step: string; message: string }
  | { type: "tool_called"; tool: string; args: Record<string, unknown>; result_summary: string }
  | { type: "question"; question_id: string; question: string; reason: string; options?: string[] }
  | { type: "completed"; result: MediaAgentResult }
  | { type: "error"; error: string }

export interface SavedOptimization {
  id: string
  original_prompt: string
  optimized_prompt: string
  task_description: string
  original_score: number
  optimized_score: number
  improvements: string[]
  reasoning: string
  analysis: PromptAnalysis | null
  skill_name: string | null
  model_used: string
  created_at: string
  // Prompt Library fields
  name: string | null
  folder: string | null
  // Media-specific fields
  media_type: "photo" | "video" | null
  target_model: string | null
  parameters: string | null
  tips: string[] | null
  web_sources: WebSourceResponse[] | null
  aspect_ratio: string | null
}

export interface Folder {
  name: string
  count: number
}

export interface UpdateOptimizationRequest {
  name?: string
  optimized_prompt?: string
  folder?: string
}

export interface SavedEvaluation {
  id: string
  eval_type: "evaluation" | "comparison"
  request: string
  response: string | null
  model_name: string | null
  response_a: string | null
  response_b: string | null
  model_a: string | null
  model_b: string | null
  judgment: Record<string, unknown> | null
  hallucination_check: Record<string, unknown> | null
  comparison_result: Record<string, unknown> | null
  hallucination_check_a: Record<string, unknown> | null
  hallucination_check_b: Record<string, unknown> | null
  created_at: string
}



// File upload types
export interface UploadedFile {
  file_name: string
  file_data: string  // base64 encoded
  mime_type: string | null
}

export interface FileProcessingResult {
  file_name: string
  file_type: string
  extracted_text: string
  extraction_method: string
  status: "success" | "error"
  error_message: string | null
}

// Media optimization types
export type MediaType = "photo" | "video"

export interface MediaOptimizeRequest {
  media_type: MediaType
  subject: string
  style_lighting?: string
  existing_prompt?: string
  // Photo-specific
  issues_to_fix?: string[]
  constraints?: string
  // Video-specific
  camera_movement?: string
  shot_type?: string
  motion_endpoints?: string
  // File upload (available to all users)
  uploaded_files?: UploadedFile[]
}

export interface MediaOptimizationResult {
  optimized_prompt: string
  original_prompt: string | null
  original_score: number | null
  optimized_score: number
  improvements: string[]
  reasoning: string
  tips: string[]
  media_type: MediaType
  file_context: FileProcessingResult[] | null
}

// Web source for research-based optimizations
export interface WebSourceResponse {
  url: string
  title: string
  content: string
}

// Media Agent types (for WebSocket-based optimization)
export type TargetModel =
  | "midjourney" | "stable_diffusion" | "dalle" | "flux"  // Photo models
  | "runway" | "luma" | "kling" | "veo"  // Video models
  | "generic"

export interface MediaAgentResult {
  original_prompt: string
  optimized_prompt: string
  parameters: string | null  // For Midjourney (--ar, --v, etc.)
  improvements: string[]
  reasoning: string
  original_score: number
  optimized_score: number
  tips: string[]
  web_sources: WebSourceResponse[]
  media_type: MediaType
  target_model: string
  analysis: Record<string, unknown> | null
}

// Billing types
export interface SubscriptionInfo {
  plan: string
  status: string
  period_end: string | null
  stripe_customer_id: string | null
}

export interface UsageInfo {
  requests_this_month: number
  optimizations_this_month: number
  requests_limit: number
  optimizations_limit: number
  tokens_used_this_month: number
  estimated_cost_cents: number
  usage_reset_at: string | null
  bonus_optimizations: number
  total_referrals: number
}

// Referral types
export interface ReferralInfo {
  referral_code: string
  referral_link: string
  total_referrals: number
  bonus_optimizations_earned: number
}

export interface ReferralHistoryItem {
  referred_email: string
  created_at: string
  reward_given: number
}

export interface ReferralHistoryResponse {
  referrals: ReferralHistoryItem[]
  total: number
}

export interface BillingInfo {
  subscription: SubscriptionInfo
  usage: UsageInfo
}

export interface CheckoutSessionResponse {
  checkout_url: string
  session_id: string
}

export interface PortalSessionResponse {
  portal_url: string
}

// Create authenticated agent API
export function createAuthenticatedAgentApi(apiKey: string) {
  const headers = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${apiKey}`,
  }

  return {
    async optimize(
      promptTemplate: string,
      taskDescription: string,
      sampleInputs?: string[],
      skillName?: string
    ): Promise<OptimizationResult> {
      const res = await fetchWithTimeout(`${API_BASE}/agents/optimize`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          prompt_template: promptTemplate,
          task_description: taskDescription,
          sample_inputs: sampleInputs || [],
          skill_name: skillName,
        }),
      }, TIMEOUTS.OPTIMIZE)
      if (!res.ok) {
        if (res.status === 429) {
          const data = await res.json()
          throw new Error(data.detail || "Optimization limit exceeded")
        }
        throw new Error("Failed to optimize prompt")
      }
      return res.json()
    },

    async saveOptimization(
      result: OptimizationResult,
      taskDescription: string,
      skillName?: string
    ): Promise<SavedOptimization> {
      const res = await fetch(`${API_BASE}/agents/optimizations`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          original_prompt: result.original_prompt,
          optimized_prompt: result.optimized_prompt,
          task_description: taskDescription,
          original_score: result.original_score,
          optimized_score: result.optimized_score,
          improvements: result.improvements,
          reasoning: result.reasoning,
          analysis: result.analysis,
          skill_name: skillName,
        }),
      })
      if (!res.ok) throw new Error("Failed to save optimization")
      return res.json()
    },

    async listOptimizations(limit = 20, offset = 0): Promise<{ optimizations: SavedOptimization[]; total: number }> {
      const res = await fetch(`${API_BASE}/agents/optimizations?limit=${limit}&offset=${offset}`, { headers })
      if (!res.ok) throw new Error("Failed to list optimizations")
      return res.json()
    },
  }
}

// Session-based authenticated API (uses cookies)
export const sessionApi = {
  async listRequests(params?: { limit?: number; offset?: number; trace_id?: string }): Promise<LoggedRequest[]> {
    const searchParams = new URLSearchParams()
    if (params?.limit) searchParams.set("limit", String(params.limit))
    if (params?.offset) searchParams.set("offset", String(params.offset))
    if (params?.trace_id) searchParams.set("trace_id", params.trace_id)

    const res = await fetch(`${API_BASE}/requests?${searchParams}`, {
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to list requests")
    return res.json()
  },

  async getRequest(id: string): Promise<LoggedRequest> {
    const res = await fetch(`${API_BASE}/requests/${id}`, {
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to get request")
    return res.json()
  },

  async evaluateRequest(id: string): Promise<LoggedRequest> {
    const res = await fetch(`${API_BASE}/requests/${id}/evaluate`, {
      method: "POST",
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to evaluate request")
    return res.json()
  },

  async getBillingInfo(): Promise<BillingInfo> {
    const res = await fetch(`${API_BASE}/billing`, {
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to get billing info")
    return res.json()
  },

  async createCheckoutSession(plan: string, billingPeriod: "monthly" | "yearly" = "monthly"): Promise<CheckoutSessionResponse> {
    const res = await fetch(`${API_BASE}/billing/checkout`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ plan, billing_period: billingPeriod }),
    })
    if (!res.ok) throw new Error("Failed to create checkout session")
    return res.json()
  },

  async createPortalSession(): Promise<PortalSessionResponse> {
    const res = await fetch(`${API_BASE}/billing/portal`, {
      method: "POST",
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to create portal session")
    return res.json()
  },

  async optimize(
    promptTemplate: string,
    taskDescription: string,
    sampleInputs?: string[],
    skillName?: string,
    uploadedFiles?: UploadedFile[],
    outputFormat?: string
  ): Promise<OptimizationResult> {
    const res = await fetchWithTimeout(`${API_BASE}/agents/optimize`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        prompt_template: promptTemplate,
        task_description: taskDescription,
        sample_inputs: sampleInputs || [],
        skill_name: skillName,
        uploaded_files: uploadedFiles || [],
        output_format: outputFormat || "auto",
      }),
    }, TIMEOUTS.OPTIMIZE)
    if (!res.ok) {
      if (res.status === 429) {
        const data = await res.json()
        throw new Error(data.detail || "Optimization limit exceeded")
      }
      if (res.status === 403) {
        const data = await res.json()
        throw new Error(data.detail || "Premium feature not available")
      }
      throw new Error("Failed to optimize prompt")
    }
    return res.json()
  },

  async saveOptimization(
    result: OptimizationResult,
    taskDescription: string,
    skillName?: string
  ): Promise<SavedOptimization> {
    const res = await fetch(`${API_BASE}/agents/optimizations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        original_prompt: result.original_prompt,
        optimized_prompt: result.optimized_prompt,
        task_description: taskDescription,
        original_score: result.original_score,
        optimized_score: result.optimized_score,
        improvements: result.improvements,
        reasoning: result.reasoning,
        analysis: result.analysis,
        skill_name: skillName,
      }),
    })
    if (!res.ok) throw new Error("Failed to save optimization")
    return res.json()
  },

  async listOptimizations(
    limit = 20,
    offset = 0,
    filters?: {
      folder?: string
      media_type?: "photo" | "video" | "text"
      target_model?: string
      search?: string
    }
  ): Promise<{ optimizations: SavedOptimization[]; total: number }> {
    const params = new URLSearchParams()
    params.set("limit", String(limit))
    params.set("offset", String(offset))
    if (filters?.folder !== undefined) params.set("folder", filters.folder)
    if (filters?.media_type) params.set("media_type", filters.media_type)
    if (filters?.target_model) params.set("target_model", filters.target_model)
    if (filters?.search) params.set("search", filters.search)

    const res = await fetch(`${API_BASE}/agents/optimizations?${params}`, {
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to list optimizations")
    return res.json()
  },

  async listFolders(): Promise<{ folders: Folder[] }> {
    const res = await fetch(`${API_BASE}/agents/optimizations/folders`, {
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to list folders")
    return res.json()
  },

  async saveMediaOptimization(
    result: MediaAgentResult,
    taskDescription: string,
    name?: string,
    folder?: string,
    aspectRatio?: string
  ): Promise<SavedOptimization> {
    const res = await fetch(`${API_BASE}/agents/optimizations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        original_prompt: result.original_prompt,
        optimized_prompt: result.optimized_prompt,
        task_description: taskDescription,
        original_score: result.original_score,
        optimized_score: result.optimized_score,
        improvements: result.improvements,
        reasoning: result.reasoning,
        name: name || taskDescription.slice(0, 100),
        folder: folder || null,
        media_type: result.media_type,
        target_model: result.target_model,
        parameters: result.parameters,
        tips: result.tips,
        web_sources: result.web_sources,
        aspect_ratio: aspectRatio,
      }),
    })
    if (!res.ok) throw new Error("Failed to save optimization")
    return res.json()
  },

  async updateOptimization(
    id: string,
    updates: UpdateOptimizationRequest
  ): Promise<SavedOptimization> {
    const res = await fetch(`${API_BASE}/agents/optimizations/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(updates),
    })
    if (!res.ok) throw new Error("Failed to update optimization")
    return res.json()
  },

  async deleteOptimization(id: string): Promise<void> {
    const res = await fetch(`${API_BASE}/agents/optimizations/${id}`, {
      method: "DELETE",
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to delete optimization")
  },

  async saveEvaluation(
    request: string,
    response: string,
    judgment: Judgment,
    modelName?: string
  ): Promise<SavedEvaluation> {
    const res = await fetch(`${API_BASE}/agents/evaluations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        request,
        response,
        model_name: modelName,
        judgment,
        hallucination_check: judgment.hallucination_check,
      }),
    })
    if (!res.ok) throw new Error("Failed to save evaluation")
    return res.json()
  },

  async saveComparison(
    request: string,
    responseA: string,
    responseB: string,
    comparisonResult: CompareResult,
    modelA?: string,
    modelB?: string
  ): Promise<SavedEvaluation> {
    const res = await fetch(`${API_BASE}/agents/comparisons`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        request,
        response_a: responseA,
        response_b: responseB,
        model_a: modelA,
        model_b: modelB,
        comparison_result: comparisonResult,
      }),
    })
    if (!res.ok) throw new Error("Failed to save comparison")
    return res.json()
  },

  async listEvaluations(limit = 20, offset = 0): Promise<{ evaluations: SavedEvaluation[]; total: number }> {
    const res = await fetch(`${API_BASE}/agents/evaluations?limit=${limit}&offset=${offset}`, {
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to list evaluations")
    return res.json()
  },

  
  async optimizeMedia(request: MediaOptimizeRequest): Promise<MediaOptimizationResult> {
    const res = await fetchWithTimeout(`${API_BASE}/agents/optimize-media`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        media_type: request.media_type,
        subject: request.subject,
        style_lighting: request.style_lighting || "",
        existing_prompt: request.existing_prompt || "",
        issues_to_fix: request.issues_to_fix || [],
        constraints: request.constraints || "",
        camera_movement: request.camera_movement || "",
        shot_type: request.shot_type || "",
        motion_endpoints: request.motion_endpoints || "",
        uploaded_files: request.uploaded_files || [],
      }),
    }, TIMEOUTS.OPTIMIZE)
    if (!res.ok) {
      if (res.status === 429) {
        const data = await res.json()
        throw new Error(data.detail || "Optimization limit exceeded")
      }
      if (res.status === 403) {
        const data = await res.json()
        throw new Error(data.detail || "Premium feature not available")
      }
      throw new Error("Failed to optimize media prompt")
    }
    return res.json()
  },

  // Agent-based optimization (WebSocket)
  async startAgentOptimization(
    promptTemplate: string,
    taskDescription: string,
    sampleInputs?: string[],
    outputFormat?: string
  ): Promise<AgentSessionResponse> {
    const res = await fetch(`${API_BASE}/agents/optimize/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        prompt_template: promptTemplate,
        task_description: taskDescription,
        sample_inputs: sampleInputs || [],
        output_format: outputFormat || "auto",
      }),
    })
    if (!res.ok) {
      if (res.status === 429) {
        const data = await res.json()
        throw new Error(data.detail || "Optimization limit exceeded")
      }
      throw new Error("Failed to start agent optimization")
    }
    return res.json()
  },

  // Media Agent-based optimization (WebSocket)
  async startMediaAgentOptimization(
    prompt: string,
    taskDescription: string,
    mediaType: "photo" | "video",
    targetModel: string,
    aspectRatio?: string,
    logoUrl?: string,
    uploadedFiles?: UploadedFile[]
  ): Promise<AgentSessionResponse> {
    const res = await fetch(`${API_BASE}/agents/media-optimize/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        prompt: prompt,
        task_description: taskDescription,
        media_type: mediaType,
        target_model: targetModel,
        aspect_ratio: aspectRatio || null,
        logo_url: logoUrl || null,
        uploaded_files: uploadedFiles || [],
      }),
    })
    if (!res.ok) {
      if (res.status === 429) {
        const data = await res.json()
        throw new Error(data.detail || "Optimization limit exceeded")
      }
      throw new Error("Failed to start media agent optimization")
    }
    return res.json()
  },

  async listApiKeys(orgId: string): Promise<ApiKey[]> {
    const res = await fetch(`${API_BASE}/admin/organizations/${orgId}/api-keys`, {
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to list API keys")
    return res.json()
  },

  async createApiKey(orgId: string, name?: string): Promise<ApiKey> {
    const res = await fetch(`${API_BASE}/admin/organizations/${orgId}/api-keys`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ name }),
    })
    if (!res.ok) throw new Error("Failed to create API key")
    return res.json()
  },

  async deleteApiKey(keyId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/admin/api-keys/${keyId}`, {
      method: "DELETE",
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to delete API key")
  },

  // Referral endpoints
  async getReferralInfo(): Promise<ReferralInfo> {
    const res = await fetch(`${API_BASE}/referral/info`, {
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to get referral info")
    return res.json()
  },

  async getReferralHistory(): Promise<ReferralHistoryResponse> {
    const res = await fetch(`${API_BASE}/referral/history`, {
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to get referral history")
    return res.json()
  },
}

// Auth API (cookie-based sessions)
export const authApi = {
  async register(email: string, password: string, name: string | null, organizationName: string, referralCode?: string): Promise<AuthResponse> {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        email,
        password,
        name,
        organization_name: organizationName,
        referral_code: referralCode || null,
      }),
    })
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      throw new Error(data.detail || "Registration failed")
    }
    return res.json()
  },

  async login(email: string, password: string): Promise<AuthResponse> {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ email, password }),
    })
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      throw new Error(data.detail || "Invalid email or password")
    }
    return res.json()
  },

  async devLogin(): Promise<AuthResponse> {
    const res = await fetch(`${API_BASE}/auth/dev-login`, {
      method: "POST",
      credentials: "include",
    })
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      throw new Error(data.detail || "Dev login failed")
    }
    return res.json()
  },

  async logout(): Promise<void> {
    await fetch(`${API_BASE}/auth/logout`, {
      method: "POST",
      credentials: "include",
    })
  },

  async getMe(): Promise<AuthResponse> {
    const res = await fetch(`${API_BASE}/auth/me`, {
      credentials: "include",
    })
    if (!res.ok) {
      throw new Error("Not authenticated")
    }
    return res.json()
  },

  async verifyEmail(token: string): Promise<{ message: string }> {
    const res = await fetch(`${API_BASE}/auth/verify-email`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ token }),
    })
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      throw new Error(data.detail || "Failed to verify email")
    }
    return res.json()
  },

  async resendVerification(email: string): Promise<{ message: string }> {
    const res = await fetch(`${API_BASE}/auth/resend-verification`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ email }),
    })
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      throw new Error(data.detail || "Failed to resend verification")
    }
    return res.json()
  },
}

// Agent API (no auth required for some endpoints)
export const agentApi = {
  async listSkills(): Promise<{ skills: Skill[]; total: number }> {
    const res = await fetch(`${API_BASE}/agents/skills`)
    if (!res.ok) throw new Error("Failed to list skills")
    return res.json()
  },

  async getSkill(name: string): Promise<Skill> {
    const res = await fetch(`${API_BASE}/agents/skills/${name}`)
    if (!res.ok) throw new Error("Failed to get skill")
    return res.json()
  },

  async createPlan(userRequest: string): Promise<Plan> {
    const res = await fetch(`${API_BASE}/agents/plan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_request: userRequest }),
    })
    if (!res.ok) throw new Error("Failed to create plan")
    return res.json()
  },

  async executeSkill(skill: string, input: string, variables?: Record<string, string>): Promise<ExecuteResult> {
    const res = await fetch(`${API_BASE}/agents/execute`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ skill, input, variables: variables || {} }),
    })
    if (!res.ok) throw new Error("Failed to execute skill")
    return res.json()
  },

  async evaluate(request: string, response: string, rubric?: string): Promise<Judgment> {
    const res = await fetchWithTimeout(`${API_BASE}/agents/evaluate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ request, response, rubric }),
    }, TIMEOUTS.LONG)
    if (!res.ok) throw new Error("Failed to evaluate")
    return res.json()
  },

  async compare(request: string, responseA: string, responseB: string, rubric?: string): Promise<CompareResult> {
    const res = await fetchWithTimeout(`${API_BASE}/agents/compare`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ request, response_a: responseA, response_b: responseB, rubric }),
    }, TIMEOUTS.LONG)
    if (!res.ok) throw new Error("Failed to compare")
    return res.json()
  },

  async analyze(promptTemplate: string, taskDescription: string): Promise<PromptAnalysis> {
    const res = await fetchWithTimeout(`${API_BASE}/agents/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt_template: promptTemplate, task_description: taskDescription }),
    }, TIMEOUTS.LONG)
    if (!res.ok) throw new Error("Failed to analyze prompt")
    return res.json()
  },

  async optimize(
    promptTemplate: string,
    taskDescription: string,
    sampleInputs?: string[],
    skillName?: string
  ): Promise<OptimizationResult> {
    const res = await fetchWithTimeout(`${API_BASE}/agents/optimize`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt_template: promptTemplate,
        task_description: taskDescription,
        sample_inputs: sampleInputs || [],
        skill_name: skillName,
      }),
    }, TIMEOUTS.OPTIMIZE)
    if (!res.ok) throw new Error("Failed to optimize prompt")
    return res.json()
  },

}


// WebSocket helper for agent-based optimization
const WS_BASE = import.meta.env.VITE_API_URL
  ? import.meta.env.VITE_API_URL.replace(/^http/, "ws")
  : "ws://localhost:8000"

export function connectAgentOptimizeWebSocket(
  sessionId: string,
  handlers: {
    onProgress?: (step: string, message: string) => void
    onToolCalled?: (tool: string, args: Record<string, unknown>, resultSummary: string) => void
    onQuestion?: (questionId: string, question: string, reason: string, options?: string[]) => void
    onCompleted?: (result: OptimizationResult) => void
    onError?: (error: string) => void
    onClose?: () => void
  }
): {
  sendAnswer: (questionId: string, answer: string) => void
  close: () => void
} {
  const ws = new WebSocket(`${WS_BASE}/ws/optimize/${sessionId}`)

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data) as AgentWebSocketMessage
      switch (data.type) {
        case "progress":
          handlers.onProgress?.(data.step, data.message)
          break
        case "tool_called":
          handlers.onToolCalled?.(data.tool, data.args, data.result_summary)
          break
        case "question":
          handlers.onQuestion?.(data.question_id, data.question, data.reason, data.options)
          break
        case "completed":
          handlers.onCompleted?.(data.result)
          break
        case "error":
          handlers.onError?.(data.error)
          break
      }
    } catch (e) {
      console.error("Failed to parse WebSocket message:", e)
    }
  }

  ws.onerror = () => {
    handlers.onError?.("WebSocket connection error")
  }

  ws.onclose = () => {
    handlers.onClose?.()
  }

  return {
    sendAnswer: (questionId: string, answer: string) => {
      ws.send(JSON.stringify({ type: "answer", question_id: questionId, answer }))
    },
    close: () => {
      ws.close()
    },
  }
}


// ============================================================================
// Video MVP Types
// ============================================================================

export interface VideoProject {
  id: string
  name: string
  description: string | null
  created_by: string | null
  created_at: string
  updated_at: string
  prompt_count: number
}

export interface VideoPrompt {
  id: string
  project_id: string
  name: string
  purpose: string | null
  target_model: string | null
  created_by: string | null
  created_at: string
  updated_at: string
  version_count: number
  latest_version_number: number | null
}

export interface VideoPromptVersion {
  id: string
  prompt_id: string
  version_number: number
  type: "main" | "variant"
  status: "active" | "draft"
  source_version_id: string | null
  created_by: string | null
  created_at: string
  scene_description: string | null
  motion_timing: string | null
  style_tone: string | null
  camera_language: string | null
  constraints: string | null
  negative_instructions: string | null
  full_prompt_text: string | null
  output_count: number
  good_count: number
  bad_count: number
  score: number
}

export interface VideoPromptOutput {
  id: string
  version_id: string
  created_by: string | null
  created_at: string
  url: string
  notes: string | null
  rating: "good" | "bad" | null
  reason_tags: string[] | null
}

export interface ShareToken {
  id: string
  prompt_id: string
  token: string | null
  created_by: string | null
  created_at: string
  expires_at: string
  revoked_at: string | null
  is_active: boolean
}

export interface VideoPromptDetail {
  prompt: VideoPrompt
  versions: VideoPromptVersion[]
  best_version_id: string | null
  share_url: string | null
}

export interface SharedVideoPrompt {
  prompt: VideoPrompt
  versions: VideoPromptVersion[]
  outputs: VideoPromptOutput[]
  best_version_id: string | null
}

export interface FeatureFlags {
  video_mvp_enabled: boolean
}

// ============================================================================
// Video MVP API
// ============================================================================

export const videoApi = {
  // Feature Flags
  async getFeatureFlags(): Promise<FeatureFlags> {
    const res = await fetch(`${API_BASE}/video/config/features`, {
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to get feature flags")
    return res.json()
  },

  // Projects
  async listProjects(): Promise<{ projects: VideoProject[]; total: number }> {
    const res = await fetch(`${API_BASE}/video/projects`, {
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to list video projects")
    return res.json()
  },

  async createProject(name: string, description?: string): Promise<VideoProject> {
    const res = await fetch(`${API_BASE}/video/projects`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ name, description }),
    })
    if (!res.ok) throw new Error("Failed to create video project")
    return res.json()
  },

  async getProject(id: string): Promise<VideoProject> {
    const res = await fetch(`${API_BASE}/video/projects/${id}`, {
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to get video project")
    return res.json()
  },

  async updateProject(id: string, data: { name?: string; description?: string }): Promise<VideoProject> {
    const res = await fetch(`${API_BASE}/video/projects/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(data),
    })
    if (!res.ok) throw new Error("Failed to update video project")
    return res.json()
  },

  async deleteProject(id: string): Promise<void> {
    const res = await fetch(`${API_BASE}/video/projects/${id}`, {
      method: "DELETE",
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to delete video project")
  },

  // Prompts
  async listPrompts(projectId: string): Promise<{ prompts: VideoPrompt[]; total: number }> {
    const res = await fetch(`${API_BASE}/video/projects/${projectId}/prompts`, {
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to list video prompts")
    return res.json()
  },

  async createPrompt(
    projectId: string,
    data: {
      name: string
      purpose?: string
      target_model?: string
      scene_description?: string
      motion_timing?: string
      style_tone?: string
      camera_language?: string
      constraints?: string
      negative_instructions?: string
    }
  ): Promise<VideoPrompt> {
    const res = await fetch(`${API_BASE}/video/projects/${projectId}/prompts`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(data),
    })
    if (!res.ok) throw new Error("Failed to create video prompt")
    return res.json()
  },

  async getPrompt(id: string): Promise<VideoPromptDetail> {
    const res = await fetch(`${API_BASE}/video/prompts/${id}`, {
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to get video prompt")
    return res.json()
  },

  async updatePrompt(
    id: string,
    data: { name?: string; purpose?: string; target_model?: string }
  ): Promise<VideoPrompt> {
    const res = await fetch(`${API_BASE}/video/prompts/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(data),
    })
    if (!res.ok) throw new Error("Failed to update video prompt")
    return res.json()
  },

  async deletePrompt(id: string): Promise<void> {
    const res = await fetch(`${API_BASE}/video/prompts/${id}`, {
      method: "DELETE",
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to delete video prompt")
  },

  // Versions
  async createVersion(
    promptId: string,
    data: {
      scene_description?: string
      motion_timing?: string
      style_tone?: string
      camera_language?: string
      constraints?: string
      negative_instructions?: string
    }
  ): Promise<VideoPromptVersion> {
    const res = await fetch(`${API_BASE}/video/prompts/${promptId}/versions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(data),
    })
    if (!res.ok) throw new Error("Failed to create version")
    return res.json()
  },

  async rollbackVersion(promptId: string, versionId: string): Promise<VideoPromptVersion> {
    const res = await fetch(`${API_BASE}/video/prompts/${promptId}/rollback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ version_id: versionId }),
    })
    if (!res.ok) throw new Error("Failed to rollback version")
    return res.json()
  },

  async generateVariants(
    promptId: string,
    count: number = 5
  ): Promise<{ versions: VideoPromptVersion[]; total: number }> {
    const res = await fetchWithTimeout(
      `${API_BASE}/video/prompts/${promptId}/generate-variants`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ count }),
      },
      TIMEOUTS.OPTIMIZE
    )
    if (!res.ok) throw new Error("Failed to generate variants")
    return res.json()
  },

  async promoteVariant(versionId: string): Promise<VideoPromptVersion> {
    const res = await fetch(`${API_BASE}/video/versions/${versionId}/promote`, {
      method: "POST",
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to promote variant")
    return res.json()
  },

  async deleteVersion(versionId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/video/versions/${versionId}`, {
      method: "DELETE",
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to delete version")
  },

  // Outputs
  async attachOutput(
    versionId: string,
    url: string,
    notes?: string
  ): Promise<VideoPromptOutput> {
    const res = await fetch(`${API_BASE}/video/versions/${versionId}/outputs`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ url, notes }),
    })
    if (!res.ok) throw new Error("Failed to attach output")
    return res.json()
  },

  async listOutputs(versionId: string): Promise<{ outputs: VideoPromptOutput[]; total: number }> {
    const res = await fetch(`${API_BASE}/video/versions/${versionId}/outputs`, {
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to list outputs")
    return res.json()
  },

  async scoreOutput(
    outputId: string,
    rating: "good" | "bad",
    reasonTags?: string[]
  ): Promise<VideoPromptOutput> {
    const res = await fetch(`${API_BASE}/video/outputs/${outputId}/score`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ rating, reason_tags: reasonTags }),
    })
    if (!res.ok) throw new Error("Failed to score output")
    return res.json()
  },

  async deleteOutput(outputId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/video/outputs/${outputId}`, {
      method: "DELETE",
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to delete output")
  },

  // Best Version
  async getBestVersion(promptId: string): Promise<VideoPromptVersion> {
    const res = await fetch(`${API_BASE}/video/prompts/${promptId}/best`, {
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to get best version")
    return res.json()
  },

  // Share Tokens
  async createShareToken(promptId: string, expiresInDays: number = 7): Promise<ShareToken> {
    const res = await fetch(`${API_BASE}/video/prompts/${promptId}/share`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ expires_in_days: expiresInDays }),
    })
    if (!res.ok) throw new Error("Failed to create share token")
    return res.json()
  },

  async listShareTokens(promptId: string): Promise<{ tokens: ShareToken[]; total: number }> {
    const res = await fetch(`${API_BASE}/video/prompts/${promptId}/shares`, {
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to list share tokens")
    return res.json()
  },

  async revokeShareToken(shareId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/video/shares/${shareId}`, {
      method: "DELETE",
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to revoke share token")
  },

  // Public Share Access (no auth required)
  async getSharedPrompt(token: string): Promise<SharedVideoPrompt> {
    const res = await fetch(`${API_BASE}/video/share/${token}`)
    if (!res.ok) {
      if (res.status === 403) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail || "Share link expired or revoked")
      }
      throw new Error("Failed to access shared prompt")
    }
    return res.json()
  },
}

// ============================================================================
// Video Workflow API (7-step wizard)
// ============================================================================

import type {
  VideoWorkflow,
  VideoWorkflowDetail,
  BriefIntake,
  ClarifyingQuestion,
  ContinuityPack,
  ShotPlan,
  Shot,
  PromptPack,
  ShotPrompt,
  QAScore,
  VersionSnapshot,
  UpdateContinuityRequest,
  UpdateShotRequest,
  UpdatePromptRequest,
  ExportWorkflowResponse,
} from "@/types/video-workflow"

export type { VideoWorkflow, VideoWorkflowDetail }

export const videoWorkflowApi = {
  // Workflow CRUD
  async create(name: string): Promise<VideoWorkflow> {
    const res = await fetch(`${API_BASE}/video-workflows`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ name }),
    })
    if (!res.ok) throw new Error("Failed to create workflow")
    return res.json()
  },

  async list(includeTemplates = false): Promise<VideoWorkflow[]> {
    const params = new URLSearchParams()
    if (includeTemplates) params.set("include_templates", "true")
    const res = await fetch(`${API_BASE}/video-workflows?${params}`, {
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to list workflows")
    return res.json()
  },

  async get(id: string): Promise<VideoWorkflowDetail> {
    const res = await fetch(`${API_BASE}/video-workflows/${id}`, {
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to get workflow")
    return res.json()
  },

  async delete(id: string): Promise<void> {
    const res = await fetch(`${API_BASE}/video-workflows/${id}`, {
      method: "DELETE",
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to delete workflow")
  },

  // Step 1-2: Brief & Questions
  async saveBrief(id: string, brief: BriefIntake): Promise<{ message: string; brief: BriefIntake }> {
    const res = await fetch(`${API_BASE}/video-workflows/${id}/brief`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(brief),
    })
    if (!res.ok) throw new Error("Failed to save brief")
    return res.json()
  },

  async generateQuestions(id: string): Promise<{ questions: ClarifyingQuestion[] }> {
    const res = await fetchWithTimeout(`${API_BASE}/video-workflows/${id}/questions`, {
      method: "POST",
      credentials: "include",
    }, TIMEOUTS.LONG)
    if (!res.ok) throw new Error("Failed to generate questions")
    return res.json()
  },

  async submitAnswers(id: string, answers: Record<string, string>): Promise<{ message: string; questions: ClarifyingQuestion[] }> {
    const res = await fetch(`${API_BASE}/video-workflows/${id}/questions/answer`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ answers }),
    })
    if (!res.ok) throw new Error("Failed to submit answers")
    return res.json()
  },

  // Step 3: Continuity Pack
  async generateContinuity(id: string): Promise<{ continuity_pack: ContinuityPack }> {
    const res = await fetchWithTimeout(`${API_BASE}/video-workflows/${id}/continuity`, {
      method: "POST",
      credentials: "include",
    }, TIMEOUTS.LONG)
    if (!res.ok) throw new Error("Failed to generate continuity pack")
    return res.json()
  },

  async updateContinuity(id: string, updates: UpdateContinuityRequest): Promise<{ continuity_pack: ContinuityPack }> {
    const res = await fetch(`${API_BASE}/video-workflows/${id}/continuity`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(updates),
    })
    if (!res.ok) throw new Error("Failed to update continuity pack")
    return res.json()
  },

  // Step 4: Shot Plan
  async generateShots(id: string): Promise<{ shot_plan: ShotPlan }> {
    const res = await fetchWithTimeout(`${API_BASE}/video-workflows/${id}/shots`, {
      method: "POST",
      credentials: "include",
    }, TIMEOUTS.LONG)
    if (!res.ok) throw new Error("Failed to generate shot plan")
    return res.json()
  },

  async updateShot(id: string, shotIndex: number, updates: UpdateShotRequest): Promise<{ shot: Shot }> {
    const res = await fetch(`${API_BASE}/video-workflows/${id}/shots/${shotIndex}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(updates),
    })
    if (!res.ok) throw new Error("Failed to update shot")
    return res.json()
  },

  // Step 5: Prompt Pack
  async generatePrompts(id: string, targetModel = "sora_2"): Promise<{ prompt_pack: PromptPack }> {
    const res = await fetchWithTimeout(`${API_BASE}/video-workflows/${id}/prompts`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ target_model: targetModel }),
    }, TIMEOUTS.LONG)
    if (!res.ok) throw new Error("Failed to generate prompts")
    return res.json()
  },

  async updatePrompt(id: string, promptIndex: number, updates: UpdatePromptRequest): Promise<{ prompt: ShotPrompt }> {
    const res = await fetch(`${API_BASE}/video-workflows/${id}/prompts/${promptIndex}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(updates),
    })
    if (!res.ok) throw new Error("Failed to update prompt")
    return res.json()
  },

  // Step 6: QA Score
  async runQA(id: string): Promise<{ qa_score: QAScore }> {
    const res = await fetch(`${API_BASE}/video-workflows/${id}/qa`, {
      method: "POST",
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to run QA scoring")
    return res.json()
  },

  // Step 7: Versions, Export, Templates
  async saveVersion(id: string, step: "brief" | "continuity" | "shots" | "prompts"): Promise<{ version: VersionSnapshot; total_versions: number }> {
    const res = await fetch(`${API_BASE}/video-workflows/${id}/versions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ step }),
    })
    if (!res.ok) throw new Error("Failed to save version")
    return res.json()
  },

  async listVersions(id: string): Promise<{ versions: VersionSnapshot[] }> {
    const res = await fetch(`${API_BASE}/video-workflows/${id}/versions`, {
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to list versions")
    return res.json()
  },

  async restoreVersion(id: string, versionIndex: number): Promise<{ message: string }> {
    const res = await fetch(`${API_BASE}/video-workflows/${id}/restore/${versionIndex}`, {
      method: "POST",
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to restore version")
    return res.json()
  },

  async export(id: string, format: "json" | "markdown" = "json"): Promise<ExportWorkflowResponse> {
    const res = await fetch(`${API_BASE}/video-workflows/${id}/export?format=${format}`, {
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to export workflow")
    return res.json()
  },

  // Templates
  async listTemplates(): Promise<VideoWorkflow[]> {
    const res = await fetch(`${API_BASE}/video-workflows/templates`, {
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to list templates")
    return res.json()
  },

  async createTemplate(id: string, templateName: string): Promise<VideoWorkflow> {
    const res = await fetch(`${API_BASE}/video-workflows/${id}/template`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ template_name: templateName }),
    })
    if (!res.ok) throw new Error("Failed to create template")
    return res.json()
  },

  async createFromTemplate(templateId: string, name: string): Promise<VideoWorkflow> {
    const res = await fetch(`${API_BASE}/video-workflows/from-template/${templateId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ name }),
    })
    if (!res.ok) throw new Error("Failed to create from template")
    return res.json()
  },
}

// WebSocket helper for media agent-based optimization
export function connectMediaAgentWebSocket(
  sessionId: string,
  handlers: {
    onProgress?: (step: string, message: string) => void
    onToolCalled?: (tool: string, args: Record<string, unknown>, resultSummary: string) => void
    onQuestion?: (questionId: string, question: string, reason: string, options?: string[]) => void
    onCompleted?: (result: MediaAgentResult) => void
    onError?: (error: string) => void
    onClose?: () => void
  }
): {
  sendAnswer: (questionId: string, answer: string) => void
  close: () => void
} {
  const ws = new WebSocket(`${WS_BASE}/ws/media-optimize/${sessionId}`)

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data) as MediaAgentWebSocketMessage
      switch (data.type) {
        case "progress":
          handlers.onProgress?.(data.step, data.message)
          break
        case "tool_called":
          handlers.onToolCalled?.(data.tool, data.args, data.result_summary)
          break
        case "question":
          handlers.onQuestion?.(data.question_id, data.question, data.reason, data.options)
          break
        case "completed":
          handlers.onCompleted?.(data.result)
          break
        case "error":
          handlers.onError?.(data.error)
          break
      }
    } catch (e) {
      console.error("Failed to parse WebSocket message:", e)
    }
  }

  ws.onerror = () => {
    handlers.onError?.("WebSocket connection error")
  }

  ws.onclose = () => {
    handlers.onClose?.()
  }

  return {
    sendAnswer: (questionId: string, answer: string) => {
      ws.send(JSON.stringify({ type: "answer", question_id: questionId, answer }))
    },
    close: () => {
      ws.close()
    },
  }
}
