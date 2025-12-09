import { useState, useEffect, useCallback } from "react"
import { useAuth } from "@/lib/auth"
import { adminApi, type ApiKey } from "@/lib/api"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { formatDate } from "@/lib/utils"
import { Plus, Trash2, Copy, Check, Key } from "lucide-react"

export function SettingsPage() {
  const { organization, apiKey: currentKey } = useAuth()
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([])
  const [loading, setLoading] = useState(true)
  const [newKeyName, setNewKeyName] = useState("")
  const [creating, setCreating] = useState(false)
  const [newKey, setNewKey] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  const fetchKeys = useCallback(async () => {
    if (!organization) return
    setLoading(true)
    try {
      const keys = await adminApi.listApiKeys(organization.id)
      setApiKeys(keys)
    } catch (err) {
      console.error("Failed to fetch API keys:", err)
    } finally {
      setLoading(false)
    }
  }, [organization])

  useEffect(() => {
    fetchKeys()
  }, [fetchKeys])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!organization) return
    setCreating(true)
    try {
      const key = await adminApi.createApiKey(organization.id, newKeyName || undefined)
      setNewKey(key.key!)
      setNewKeyName("")
      fetchKeys()
    } catch (err) {
      console.error("Failed to create API key:", err)
    } finally {
      setCreating(false)
    }
  }

  const handleDelete = async (keyId: string) => {
    if (!confirm("Are you sure you want to delete this API key?")) return
    try {
      await adminApi.deleteApiKey(keyId)
      fetchKeys()
    } catch (err) {
      console.error("Failed to delete API key:", err)
    }
  }

  const copyToClipboard = () => {
    if (newKey) {
      navigator.clipboard.writeText(newKey)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <div className="p-6 space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-muted-foreground">Manage your organization and API keys</p>
      </div>

      {/* Organization Info */}
      <Card>
        <CardHeader>
          <CardTitle>Organization</CardTitle>
          <CardDescription>Your organization details</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div>
              <p className="text-sm text-muted-foreground">Name</p>
              <p className="font-medium">{organization?.name}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">ID</p>
              <p className="font-mono text-sm">{organization?.id}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* New Key Created */}
      {newKey && (
        <Card className="border-green-200 bg-green-50">
          <CardHeader>
            <CardTitle className="text-green-800">API Key Created</CardTitle>
            <CardDescription className="text-green-700">
              Save this key now - it won't be shown again
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <code className="flex-1 p-3 bg-white rounded border font-mono text-sm break-all">
                {newKey}
              </code>
              <Button variant="outline" size="icon" onClick={copyToClipboard}>
                {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
              </Button>
            </div>
            <Button
              variant="ghost"
              size="sm"
              className="mt-2"
              onClick={() => setNewKey(null)}
            >
              Dismiss
            </Button>
          </CardContent>
        </Card>
      )}

      {/* API Keys */}
      <Card>
        <CardHeader>
          <CardTitle>API Keys</CardTitle>
          <CardDescription>Manage API keys for your organization</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Create new key */}
          <form onSubmit={handleCreate} className="flex gap-2">
            <Input
              placeholder="Key name (optional)"
              value={newKeyName}
              onChange={(e) => setNewKeyName(e.target.value)}
              className="max-w-xs"
            />
            <Button type="submit" disabled={creating}>
              <Plus className="h-4 w-4 mr-2" />
              {creating ? "Creating..." : "Create Key"}
            </Button>
          </form>

          {/* Key list */}
          <div className="space-y-2">
            {loading ? (
              <p className="text-muted-foreground text-sm">Loading...</p>
            ) : apiKeys.length === 0 ? (
              <p className="text-muted-foreground text-sm">No API keys found</p>
            ) : (
              apiKeys.map((key) => (
                <div
                  key={key.id}
                  className="flex items-center justify-between p-3 border rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <Key className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{key.name || "Unnamed"}</span>
                        {currentKey?.id === key.id && (
                          <Badge variant="success">Current</Badge>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground font-mono">
                        {key.key_prefix}...
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right text-sm">
                      <p className="text-muted-foreground">Created</p>
                      <p>{formatDate(key.created_at)}</p>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDelete(key.id)}
                      className="text-destructive hover:text-destructive"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>

      {/* SDK Usage */}
      <Card>
        <CardHeader>
          <CardTitle>SDK Usage</CardTitle>
          <CardDescription>Quick start guide for the Python SDK</CardDescription>
        </CardHeader>
        <CardContent>
          <pre className="p-4 bg-muted rounded-lg text-sm overflow-x-auto">
{`from promptlab import PromptLab, track
from openai import OpenAI

# Option 1: Track OpenAI client
client = track(OpenAI(), api_key="your_api_key")
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Option 2: Manual logging
lab = PromptLab(api_key="your_api_key")
lab.api.log_request({
    "model": "gpt-4",
    "provider": "openai",
    "messages": [...],
    "response_content": "...",
    "latency_ms": 100,
})`}
          </pre>
        </CardContent>
      </Card>
    </div>
  )
}
