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
}

export interface ToolCallInfo {
  tool: string
  args: Record<string, unknown>
  result_summary: string
}

export type AgentWebSocketMessage =
  | { type: "progress"; step: string; message: string }
  | { type: "tool_called"; tool: string; args: Record<string, unknown>; result_summary: string }
  | { type: "question"; question_id: string; question: string; reason: string }
  | { type: "completed"; result: OptimizationResult }
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
  // File upload (Premium/Pro only)
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

  async listOptimizations(limit = 20, offset = 0): Promise<{ optimizations: SavedOptimization[]; total: number }> {
    const res = await fetch(`${API_BASE}/agents/optimizations?limit=${limit}&offset=${offset}`, {
      credentials: "include",
    })
    if (!res.ok) throw new Error("Failed to list optimizations")
    return res.json()
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
    onQuestion?: (questionId: string, question: string, reason: string) => void
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
          handlers.onQuestion?.(data.question_id, data.question, data.reason)
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
