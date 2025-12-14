const API_BASE = "http://localhost:8000/api/v1"

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

export interface OptimizationResult {
  original_prompt: string
  optimized_prompt: string
  original_score: number
  optimized_score: number
  improvements: string[]
  reasoning: string
  analysis: PromptAnalysis | null
}

// Agent API (no auth required for now)
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
