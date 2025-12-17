import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { agentApi } from "@/lib/api"
import type { SavedOptimization } from "@/lib/api"
import { Loader2, Sparkles, ArrowRight, ChevronDown, ChevronUp, Copy, CheckCircle } from "lucide-react"

export function OptimizationsPage() {
  const [optimizations, setOptimizations] = useState<SavedOptimization[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [copiedId, setCopiedId] = useState<string | null>(null)

  useEffect(() => {
    loadOptimizations()
  }, [])

  const loadOptimizations = async () => {
    setLoading(true)
    try {
      const result = await agentApi.listOptimizations(50, 0)
      setOptimizations(result.optimizations)
      setTotal(result.total)
    } catch (error) {
      console.error("Failed to load optimizations:", error)
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString()
  }

  const getScoreColor = (score: number) => {
    if (score >= 8) return "text-green-600"
    if (score >= 5) return "text-yellow-600"
    return "text-red-600"
  }

  const getImprovementBadge = (original: number, optimized: number) => {
    const diff = optimized - original
    const percent = ((diff / original) * 100).toFixed(0)
    if (diff > 0) {
      return <Badge className="bg-green-100 text-green-800">+{diff.toFixed(1)} ({percent}%)</Badge>
    }
    return <Badge variant="secondary">No change</Badge>
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Sparkles className="h-8 w-8 text-primary" />
            Saved Optimizations
          </h1>
          <p className="text-muted-foreground mt-1">
            {total} optimization{total !== 1 ? "s" : ""} saved
          </p>
        </div>
        <Button onClick={loadOptimizations} variant="outline">
          Refresh
        </Button>
      </div>

      {optimizations.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Sparkles className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium">No optimizations yet</h3>
            <p className="text-muted-foreground mt-1">
              Go to the Agents page to optimize prompts and save them here.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {optimizations.map((opt) => (
            <Card key={opt.id} className="overflow-hidden">
              <CardHeader
                className="cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => setExpandedId(expandedId === opt.id ? null : opt.id)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-base flex items-center gap-2">
                      <span className="truncate max-w-md">
                        {opt.task_description}
                      </span>
                      {getImprovementBadge(opt.original_score, opt.optimized_score)}
                    </CardTitle>
                    <CardDescription className="mt-1 flex items-center gap-4">
                      <span className="flex items-center gap-1">
                        Score:
                        <span className={getScoreColor(opt.original_score)}>{opt.original_score.toFixed(1)}</span>
                        <ArrowRight className="h-3 w-3" />
                        <span className={getScoreColor(opt.optimized_score)}>{opt.optimized_score.toFixed(1)}</span>
                      </span>
                      <span>|</span>
                      <span>{formatDate(opt.created_at)}</span>
                      <span>|</span>
                      <span>{opt.model_used}</span>
                    </CardDescription>
                  </div>
                  <Button variant="ghost" size="sm">
                    {expandedId === opt.id ? (
                      <ChevronUp className="h-4 w-4" />
                    ) : (
                      <ChevronDown className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </CardHeader>

              {expandedId === opt.id && (
                <CardContent className="border-t pt-4 space-y-4">
                  {/* Original vs Optimized */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="text-sm font-medium text-muted-foreground">Original Prompt</h4>
                        <span className={`text-sm font-medium ${getScoreColor(opt.original_score)}`}>
                          Score: {opt.original_score.toFixed(1)}
                        </span>
                      </div>
                      <div className="bg-muted p-3 rounded-lg text-sm font-mono whitespace-pre-wrap max-h-64 overflow-auto">
                        {opt.original_prompt}
                      </div>
                    </div>
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="text-sm font-medium text-muted-foreground">Optimized Prompt</h4>
                        <span className={`text-sm font-medium ${getScoreColor(opt.optimized_score)}`}>
                          Score: {opt.optimized_score.toFixed(1)}
                        </span>
                      </div>
                      <div className="bg-green-50 dark:bg-green-950/20 p-3 rounded-lg text-sm font-mono whitespace-pre-wrap max-h-64 overflow-auto border border-green-200 dark:border-green-800">
                        {opt.optimized_prompt}
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        className="mt-2"
                        onClick={() => copyToClipboard(opt.optimized_prompt, opt.id)}
                      >
                        {copiedId === opt.id ? (
                          <>
                            <CheckCircle className="h-4 w-4 mr-2 text-green-600" />
                            Copied!
                          </>
                        ) : (
                          <>
                            <Copy className="h-4 w-4 mr-2" />
                            Copy Optimized
                          </>
                        )}
                      </Button>
                    </div>
                  </div>

                  {/* Improvements */}
                  {opt.improvements.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-muted-foreground mb-2">Improvements Made</h4>
                      <ul className="space-y-1">
                        {opt.improvements.map((improvement, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm">
                            <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                            {improvement}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Reasoning */}
                  {opt.reasoning && (
                    <div>
                      <h4 className="text-sm font-medium text-muted-foreground mb-2">Reasoning</h4>
                      <p className="text-sm">{opt.reasoning}</p>
                    </div>
                  )}

                  {/* Analysis */}
                  {opt.analysis && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {opt.analysis.issues.length > 0 && (
                        <div>
                          <h4 className="text-sm font-medium text-red-600 mb-2">Issues Found</h4>
                          <div className="space-y-2">
                            {opt.analysis.issues.map((issue, i) => (
                              <div key={i} className="text-sm p-2 bg-red-50 dark:bg-red-950/20 rounded border border-red-200 dark:border-red-800">
                                <div className="flex gap-2 mb-1">
                                  <Badge variant="outline" className="text-xs">{issue.category}</Badge>
                                  <Badge
                                    variant={issue.severity === "high" ? "destructive" : "secondary"}
                                    className="text-xs"
                                  >
                                    {issue.severity}
                                  </Badge>
                                </div>
                                <p>{issue.description}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      {opt.analysis.strengths.length > 0 && (
                        <div>
                          <h4 className="text-sm font-medium text-green-600 mb-2">Strengths</h4>
                          <ul className="list-disc list-inside text-sm space-y-1">
                            {opt.analysis.strengths.map((s, i) => (
                              <li key={i}>{s}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </CardContent>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
