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
  }
}
