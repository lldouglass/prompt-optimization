import { useState, useEffect, useCallback } from "react"
import { useNavigate } from "react-router-dom"
import { useAuth } from "@/lib/auth"
import { createAuthenticatedApi, type LoggedRequest } from "@/lib/api"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { formatDate, formatNumber } from "@/lib/utils"
import { RefreshCw, MessageSquare, Clock, Coins, Star } from "lucide-react"

export function DashboardPage() {
  const navigate = useNavigate()
  const { rawApiKey } = useAuth()
  const [requests, setRequests] = useState<LoggedRequest[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedRequest, setSelectedRequest] = useState<LoggedRequest | null>(null)

  const fetchRequests = useCallback(async () => {
    if (!rawApiKey) return
    setLoading(true)
    try {
      const api = createAuthenticatedApi(rawApiKey)
      const data = await api.listRequests({ limit: 50 })
      setRequests(data)
    } catch (err) {
      console.error("Failed to fetch requests:", err)
    } finally {
      setLoading(false)
    }
  }, [rawApiKey])

  const handleEvaluateInAgents = () => {
    if (!selectedRequest) return

    // Extract user message and response for the Judge
    const userMessage = selectedRequest.messages.find(m => m.role === "user")?.content || ""
    const response = selectedRequest.response_content || ""

    // Navigate to Agents page with state to auto-run evaluation
    navigate("/agents", {
      state: {
        autoEvaluate: true,
        request: userMessage,
        response: response,
      }
    })
  }

  useEffect(() => {
    fetchRequests()
  }, [fetchRequests])

  const evaluatedRequests = requests.filter((r) => r.evaluation_score != null)
  const stats = {
    total: requests.length,
    totalTokens: requests.reduce((sum, r) => sum + (r.input_tokens || 0) + (r.output_tokens || 0), 0),
    avgLatency: requests.length
      ? Math.round(requests.reduce((sum, r) => sum + (r.latency_ms || 0), 0) / requests.length)
      : 0,
    avgScore: evaluatedRequests.length
      ? (evaluatedRequests.reduce((sum, r) => sum + (r.evaluation_score || 0), 0) / evaluatedRequests.length).toFixed(1)
      : null,
    evaluated: evaluatedRequests.length,
  }

  const getScoreColor = (score: number) => {
    if (score >= 8) return "text-green-600 bg-green-50"
    if (score >= 6) return "text-yellow-600 bg-yellow-50"
    return "text-red-600 bg-red-50"
  }

  const getScoreBadgeVariant = (score: number): "default" | "secondary" | "destructive" | "outline" => {
    if (score >= 8) return "default"
    if (score >= 6) return "secondary"
    return "destructive"
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Requests</h1>
          <p className="text-muted-foreground">View logged LLM requests</p>
        </div>
        <Button variant="outline" size="sm" onClick={fetchRequests} disabled={loading}>
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Requests</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatNumber(stats.total)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Avg Quality Score</CardTitle>
            <Star className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats.avgScore ? `${stats.avgScore}/10` : "-"}
            </div>
            <p className="text-xs text-muted-foreground">
              {stats.evaluated} of {stats.total} evaluated
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Tokens</CardTitle>
            <Coins className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatNumber(stats.totalTokens)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Avg Latency</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatNumber(stats.avgLatency)}ms</div>
          </CardContent>
        </Card>
      </div>

      {/* Request List & Detail */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* List */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Requests</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {loading ? (
              <div className="p-6 text-center text-muted-foreground">Loading...</div>
            ) : requests.length === 0 ? (
              <div className="p-6 text-center text-muted-foreground">
                No requests yet. Use the SDK to start logging.
              </div>
            ) : (
              <div className="divide-y max-h-[500px] overflow-auto">
                {requests.map((req) => (
                  <button
                    key={req.id}
                    onClick={() => setSelectedRequest(req)}
                    className={`w-full p-4 text-left hover:bg-muted/50 transition-colors ${
                      selectedRequest?.id === req.id ? "bg-muted" : ""
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <Badge variant="secondary">{req.model}</Badge>
                        {req.evaluation_score != null && (
                          <Badge variant={getScoreBadgeVariant(req.evaluation_score)}>
                            {req.evaluation_score.toFixed(1)}/10
                          </Badge>
                        )}
                      </div>
                      <span className="text-xs text-muted-foreground">
                        {formatDate(req.created_at)}
                      </span>
                    </div>
                    <p className="text-sm truncate text-muted-foreground">
                      {req.messages[req.messages.length - 1]?.content || "No message"}
                    </p>
                    <div className="flex gap-3 mt-2 text-xs text-muted-foreground">
                      <span>{req.latency_ms}ms</span>
                      <span>{(req.input_tokens || 0) + (req.output_tokens || 0)} tokens</span>
                      {req.evaluation_tags && req.evaluation_tags.length > 0 && (
                        <span className="text-primary">{req.evaluation_tags.join(", ")}</span>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Detail */}
        <Card>
          <CardHeader>
            <CardTitle>Request Detail</CardTitle>
          </CardHeader>
          <CardContent>
            {selectedRequest ? (
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <Badge>{selectedRequest.model}</Badge>
                  <Badge variant="outline">{selectedRequest.provider}</Badge>
                  {selectedRequest.trace_id && (
                    <Badge variant="secondary">trace: {selectedRequest.trace_id}</Badge>
                  )}
                </div>

                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">Latency</p>
                    <p className="font-medium">{selectedRequest.latency_ms}ms</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Input Tokens</p>
                    <p className="font-medium">{selectedRequest.input_tokens || "-"}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Output Tokens</p>
                    <p className="font-medium">{selectedRequest.output_tokens || "-"}</p>
                  </div>
                </div>

                <div>
                  <p className="text-sm font-medium mb-2">Messages</p>
                  <div className="space-y-2 max-h-[200px] overflow-auto">
                    {selectedRequest.messages.map((msg, i) => (
                      <div
                        key={i}
                        className={`p-3 rounded-lg text-sm ${
                          msg.role === "user"
                            ? "bg-primary/10 ml-4"
                            : msg.role === "assistant"
                            ? "bg-muted mr-4"
                            : "bg-muted/50"
                        }`}
                      >
                        <p className="text-xs font-medium text-muted-foreground mb-1">
                          {msg.role}
                        </p>
                        <p className="whitespace-pre-wrap">{msg.content}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {selectedRequest.response_content && (
                  <div>
                    <p className="text-sm font-medium mb-2">Response</p>
                    <div className="p-3 rounded-lg bg-green-50 text-sm max-h-[150px] overflow-auto">
                      <p className="whitespace-pre-wrap">{selectedRequest.response_content}</p>
                    </div>
                  </div>
                )}

                {/* Evaluation Section */}
                {selectedRequest.evaluation_score != null ? (
                  <div className="border-t pt-4">
                    <div className="flex items-center justify-between mb-3">
                      <p className="text-sm font-medium">Auto-Evaluation</p>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={handleEvaluateInAgents}
                        title="Re-evaluate in Agents"
                      >
                        <RefreshCw className="h-4 w-4" />
                      </Button>
                    </div>
                    <div className={`p-3 rounded-lg ${getScoreColor(selectedRequest.evaluation_score)}`}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-lg font-bold">
                          Score: {selectedRequest.evaluation_score.toFixed(1)}/10
                        </span>
                        {selectedRequest.evaluation_tags && selectedRequest.evaluation_tags.length > 0 && (
                          <div className="flex gap-1">
                            {selectedRequest.evaluation_tags.map((tag) => (
                              <Badge key={tag} variant="outline" className="text-xs">
                                {tag}
                              </Badge>
                            ))}
                          </div>
                        )}
                      </div>

                      {selectedRequest.evaluation_subscores && (
                        <div className="grid grid-cols-4 gap-2 mb-3 text-xs">
                          {Object.entries(selectedRequest.evaluation_subscores).map(([key, value]) => (
                            <div key={key} className="text-center">
                              <p className="font-medium capitalize">{key.replace(/_/g, " ")}</p>
                              <p>{value}</p>
                            </div>
                          ))}
                        </div>
                      )}

                      {selectedRequest.evaluation_rationale && (
                        <p className="text-sm">{selectedRequest.evaluation_rationale}</p>
                      )}
                    </div>
                  </div>
                ) : selectedRequest.response_content ? (
                  <div className="border-t pt-4">
                    <div className="flex items-center justify-between">
                      <p className="text-sm text-muted-foreground">
                        Not yet evaluated
                      </p>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={handleEvaluateInAgents}
                      >
                        <Star className="h-4 w-4 mr-2" />
                        Evaluate
                      </Button>
                    </div>
                  </div>
                ) : null}
              </div>
            ) : (
              <p className="text-muted-foreground text-center py-8">
                Select a request to view details
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
