import { useState, useEffect, useCallback } from "react"
import { useSearchParams } from "react-router-dom"
import { useAuth } from "@/lib/auth"
import { sessionApi, type ApiKey, type BillingInfo } from "@/lib/api"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { formatDate } from "@/lib/utils"
import { Plus, Trash2, Copy, Check, Key, CreditCard, Sparkles, AlertCircle, ExternalLink } from "lucide-react"
import { track } from "@/lib/analytics"

export function SettingsPage() {
  const { organization } = useAuth()
  const [searchParams] = useSearchParams()
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([])
  const [loading, setLoading] = useState(true)
  const [newKeyName, setNewKeyName] = useState("")
  const [creating, setCreating] = useState(false)
  const [newKey, setNewKey] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  // Billing state
  const [billing, setBilling] = useState<BillingInfo | null>(null)
  const [billingLoading, setBillingLoading] = useState(true)
  const [upgrading, setUpgrading] = useState<string | null>(null)

  const checkoutStatus = searchParams.get("checkout")

  const fetchKeys = useCallback(async () => {
    if (!organization) return
    setLoading(true)
    try {
      const keys = await sessionApi.listApiKeys(organization.id)
      setApiKeys(keys)
    } catch (err) {
      console.error("Failed to fetch API keys:", err)
    } finally {
      setLoading(false)
    }
  }, [organization])

  const fetchBilling = useCallback(async () => {
    setBillingLoading(true)
    try {
      const info = await sessionApi.getBillingInfo()
      setBilling(info)
    } catch (err) {
      console.error("Failed to fetch billing info:", err)
    } finally {
      setBillingLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchKeys()
    fetchBilling()
  }, [fetchKeys, fetchBilling])

  const handleUpgrade = async (plan: string) => {
    setUpgrading(plan)
    // Track upgrade click
    track('upgrade_clicked', {
      plan,
      current_plan: billing?.subscription.plan || 'free',
    })
    try {
      const { checkout_url } = await sessionApi.createCheckoutSession(plan)
      window.location.href = checkout_url
    } catch (err) {
      console.error("Failed to create checkout:", err)
      alert("Failed to start checkout. Please try again.")
    } finally {
      setUpgrading(null)
    }
  }

  const handleManageBilling = async () => {
    try {
      const { portal_url } = await sessionApi.createPortalSession()
      window.location.href = portal_url
    } catch (err) {
      console.error("Failed to open billing portal:", err)
      alert("Failed to open billing portal. Please try again.")
    }
  }

  const getUsagePercent = (used: number, limit: number) => {
    if (limit === -1) return 0 // unlimited
    return Math.min((used / limit) * 100, 100)
  }

  const formatLimit = (limit: number) => {
    if (limit === -1) return "Unlimited"
    return limit.toLocaleString()
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!organization) return
    setCreating(true)
    try {
      const key = await sessionApi.createApiKey(organization.id, newKeyName || undefined)
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
      await sessionApi.deleteApiKey(keyId)
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
        <p className="text-muted-foreground">Manage your organization, billing, and API keys</p>
      </div>

      {/* Checkout Status */}
      {checkoutStatus === "success" && (
        <Card className="border-green-200 bg-green-50">
          <CardContent className="py-4">
            <div className="flex items-center gap-2 text-green-800">
              <Check className="h-5 w-5" />
              <span className="font-medium">Payment successful! Your subscription is now active.</span>
            </div>
          </CardContent>
        </Card>
      )}
      {checkoutStatus === "canceled" && (
        <Card className="border-yellow-200 bg-yellow-50">
          <CardContent className="py-4">
            <div className="flex items-center gap-2 text-yellow-800">
              <AlertCircle className="h-5 w-5" />
              <span className="font-medium">Checkout was canceled. No changes were made to your subscription.</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Billing & Subscription */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CreditCard className="h-5 w-5" />
            Subscription & Billing
          </CardTitle>
          <CardDescription>Manage your plan and view usage</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {billingLoading ? (
            <p className="text-muted-foreground">Loading billing info...</p>
          ) : billing ? (
            <>
              {/* Current Plan */}
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-lg capitalize">{billing.subscription.plan === "team" ? "Premium" : billing.subscription.plan}</span>
                    <Badge variant={billing.subscription.status === "active" ? "default" : "destructive"}>
                      {billing.subscription.status}
                    </Badge>
                  </div>
                  {billing.subscription.period_end && (
                    <p className="text-sm text-muted-foreground">
                      {billing.subscription.status === "active" ? "Renews" : "Ends"}{" "}
                      {formatDate(billing.subscription.period_end)}
                    </p>
                  )}
                </div>
                {billing.subscription.plan !== "free" && billing.subscription.stripe_customer_id && (
                  <Button variant="outline" onClick={handleManageBilling}>
                    Manage Billing <ExternalLink className="h-4 w-4 ml-2" />
                  </Button>
                )}
              </div>

              {/* Usage */}
              <div className="space-y-4">
                <h4 className="font-medium">Usage This Month</h4>
                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>API Requests</span>
                      <span>
                        {billing.usage.requests_this_month.toLocaleString()} / {formatLimit(billing.usage.requests_limit)}
                      </span>
                    </div>
                    <Progress
                      value={getUsagePercent(billing.usage.requests_this_month, billing.usage.requests_limit)}
                      className="h-2"
                    />
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Prompt Optimizations</span>
                      <span>
                        {billing.usage.optimizations_this_month.toLocaleString()} / {formatLimit(billing.usage.optimizations_limit)}
                      </span>
                    </div>
                    <Progress
                      value={getUsagePercent(billing.usage.optimizations_this_month, billing.usage.optimizations_limit)}
                      className="h-2"
                    />
                  </div>
                </div>

                {/* Token Usage & Cost (admin view) */}
                {(billing.usage.tokens_used_this_month > 0 || billing.usage.estimated_cost_cents > 0) && (
                  <div className="mt-4 p-3 bg-muted/50 rounded-lg">
                    <h5 className="text-sm font-medium mb-2">LLM Usage (Your Cost)</h5>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Tokens Used</span>
                        <p className="font-mono">{billing.usage.tokens_used_this_month.toLocaleString()}</p>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Estimated Cost</span>
                        <p className="font-mono">${(billing.usage.estimated_cost_cents / 100).toFixed(2)}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Upgrade Options */}
              {billing.subscription.plan !== "pro" && (
                <div className="space-y-3">
                  <h4 className="font-medium">Upgrade Your Plan</h4>
                  <div className={`grid grid-cols-1 ${billing.subscription.plan === "free" ? "md:grid-cols-2" : ""} gap-4`}>
                    {billing.subscription.plan === "free" && (
                      <div className="p-4 border rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-semibold">Premium</span>
                          <span className="text-lg font-bold">$15/mo</span>
                        </div>
                        <ul className="text-sm text-muted-foreground space-y-1 mb-4">
                          <li>25,000 requests/month</li>
                          <li>200 optimizations/month</li>
                          <li>30-day data retention</li>
                        </ul>
                        <Button
                          className="w-full"
                          variant="outline"
                          onClick={() => handleUpgrade("team")}
                          disabled={upgrading === "team"}
                        >
                          <Sparkles className="h-4 w-4 mr-2" />
                          {upgrading === "team" ? "Loading..." : "Upgrade to Premium"}
                        </Button>
                      </div>
                    )}
                    <div className="p-4 border-2 border-primary rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold">Pro</span>
                          <Badge>Popular</Badge>
                        </div>
                        <span className="text-lg font-bold">$90/mo</span>
                      </div>
                      <ul className="text-sm text-muted-foreground space-y-1 mb-4">
                        <li>100,000 requests/month</li>
                        <li>Unlimited optimizations</li>
                        <li>90-day data retention</li>
                      </ul>
                      <Button
                        className="w-full"
                        onClick={() => handleUpgrade("pro")}
                        disabled={upgrading === "pro"}
                      >
                        <Sparkles className="h-4 w-4 mr-2" />
                        {upgrading === "pro" ? "Loading..." : "Upgrade to Pro"}
                      </Button>
                    </div>
                  </div>
                </div>
              )}
            </>
          ) : (
            <p className="text-muted-foreground">Unable to load billing information</p>
          )}
        </CardContent>
      </Card>

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
{`from clarynt import Clarynt, track
from openai import OpenAI

# Option 1: Track OpenAI client
client = track(OpenAI(), api_key="your_api_key")
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Option 2: Manual logging
lab = Clarynt(api_key="your_api_key")
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
