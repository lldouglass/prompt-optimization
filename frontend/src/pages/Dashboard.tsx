import { useState, useEffect, useCallback } from "react"
import { useAuth } from "@/lib/auth"
import { createAuthenticatedApi, type LoggedRequest } from "@/lib/api"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { formatDate, formatNumber } from "@/lib/utils"
import { RefreshCw, MessageSquare, Clock, Coins } from "lucide-react"

export function DashboardPage() {
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

  useEffect(() => {
    fetchRequests()
  }, [fetchRequests])

  const stats = {
    total: requests.length,
    totalTokens: requests.reduce((sum, r) => sum + (r.input_tokens || 0) + (r.output_tokens || 0), 0),
    avgLatency: requests.length
      ? Math.round(requests.reduce((sum, r) => sum + (r.latency_ms || 0), 0) / requests.length)
      : 0,
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
      <div className="grid gap-4 md:grid-cols-3">
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
                      <Badge variant="secondary">{req.model}</Badge>
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
