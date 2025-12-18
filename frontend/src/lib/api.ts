const API_BASE = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api/v1`
  : "http://localhost:8000/api/v1"

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

    async createCheckoutSession(plan: string): Promise<CheckoutSessionResponse> {
      const res = await fetch(`${API_BASE}/billing/checkout`, {
        method: "POST",
        headers,
        body: JSON.stringify({ plan }),
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

export interface Judgment {
  scores: Record<string, number>
  overall_score: number
  passed: boolean
  strengths: string[]
  weaknesses: string[]
  reasoning: string
}

export interface CompareResult {
  winner: string
  confidence: string
  comparison: Record<string, { winner: string; explanation: string }>
  reasoning: string
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
}

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
  usage_reset_at: string | null
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
      const res = await fetch(`${API_BASE}/agents/optimize`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          prompt_template: promptTemplate,
          task_description: taskDescription,
          sample_inputs: sampleInputs || [],
          skill_name: skillName,
        }),
      })
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

  async createCheckoutSession(plan: string): Promise<CheckoutSessionResponse> {
    const res = await fetch(`${API_BASE}/billing/checkout`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ plan }),
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
    skillName?: string
  ): Promise<OptimizationResult> {
    const res = await fetch(`${API_BASE}/agents/optimize`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        prompt_template: promptTemplate,
        task_description: taskDescription,
        sample_inputs: sampleInputs || [],
        skill_name: skillName,
      }),
    })
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
}

// Auth API (cookie-based sessions)
export const authApi = {
  async register(email: string, password: string, name: string | null, organizationName: string): Promise<AuthResponse> {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        email,
        password,
        name,
        organization_name: organizationName,
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
    const res = await fetch(`${API_BASE}/agents/evaluate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ request, response, rubric }),
    })
    if (!res.ok) throw new Error("Failed to evaluate")
    return res.json()
  },

  async compare(request: string, responseA: string, responseB: string, rubric?: string): Promise<CompareResult> {
    const res = await fetch(`${API_BASE}/agents/compare`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ request, response_a: responseA, response_b: responseB, rubric }),
    })
    if (!res.ok) throw new Error("Failed to compare")
    return res.json()
  },

  async analyze(promptTemplate: string, taskDescription: string): Promise<PromptAnalysis> {
    const res = await fetch(`${API_BASE}/agents/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt_template: promptTemplate, task_description: taskDescription }),
    })
    if (!res.ok) throw new Error("Failed to analyze prompt")
    return res.json()
  },

  async optimize(
    promptTemplate: string,
    taskDescription: string,
    sampleInputs?: string[],
    skillName?: string
  ): Promise<OptimizationResult> {
    const res = await fetch(`${API_BASE}/agents/optimize`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt_template: promptTemplate,
        task_description: taskDescription,
        sample_inputs: sampleInputs || [],
        skill_name: skillName,
      }),
    })
    if (!res.ok) throw new Error("Failed to optimize prompt")
    return res.json()
  },

}
