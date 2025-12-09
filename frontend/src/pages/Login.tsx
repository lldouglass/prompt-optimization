import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { useAuth } from "@/lib/auth"
import { adminApi } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { Zap } from "lucide-react"

export function LoginPage() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [mode, setMode] = useState<"login" | "create">("login")
  const [apiKey, setApiKey] = useState("")
  const [orgName, setOrgName] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [createdKey, setCreatedKey] = useState("")

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)

    try {
      // Try to fetch requests to validate the key
      const res = await fetch("http://localhost:8000/api/v1/requests?limit=1", {
        headers: { Authorization: `Bearer ${apiKey}` },
      })

      if (!res.ok) {
        throw new Error("Invalid API key")
      }

      // We don't have org info from this endpoint, create a placeholder
      login(
        { id: "unknown", name: "Organization", created_at: new Date().toISOString() },
        { id: "unknown", key_prefix: apiKey.slice(0, 16), name: null, created_at: new Date().toISOString(), last_used_at: null },
        apiKey
      )
      navigate("/")
    } catch {
      setError("Invalid API key. Please check and try again.")
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)

    try {
      const org = await adminApi.createOrganization(orgName)
      const key = await adminApi.createApiKey(org.id, "Default Key")

      setCreatedKey(key.key!)
      login(org, key, key.key!)
    } catch {
      setError("Failed to create organization. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  if (createdKey) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-muted/30 p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="mx-auto mb-4 h-12 w-12 rounded-full bg-green-100 flex items-center justify-center">
              <Zap className="h-6 w-6 text-green-600" />
            </div>
            <CardTitle>Organization Created!</CardTitle>
            <CardDescription>
              Save your API key now - it won't be shown again
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="bg-muted p-3 rounded-md font-mono text-sm break-all">
              {createdKey}
            </div>
          </CardContent>
          <CardFooter>
            <Button className="w-full" onClick={() => navigate("/")}>
              Continue to Dashboard
            </Button>
          </CardFooter>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/30 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 flex items-center gap-2">
            <Zap className="h-8 w-8 text-primary" />
            <span className="text-2xl font-bold">PromptLab</span>
          </div>
          <CardDescription>
            {mode === "login" ? "Sign in with your API key" : "Create a new organization"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {mode === "login" ? (
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <Input
                  type="password"
                  placeholder="pl_live_..."
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  required
                />
              </div>
              {error && <p className="text-sm text-destructive">{error}</p>}
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? "Signing in..." : "Sign in"}
              </Button>
            </form>
          ) : (
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <Input
                  type="text"
                  placeholder="Organization name"
                  value={orgName}
                  onChange={(e) => setOrgName(e.target.value)}
                  required
                />
              </div>
              {error && <p className="text-sm text-destructive">{error}</p>}
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? "Creating..." : "Create Organization"}
              </Button>
            </form>
          )}
        </CardContent>
        <CardFooter className="justify-center">
          <Button
            variant="link"
            onClick={() => {
              setMode(mode === "login" ? "create" : "login")
              setError("")
            }}
          >
            {mode === "login" ? "Create new organization" : "Already have an API key?"}
          </Button>
        </CardFooter>
      </Card>
    </div>
  )
}
