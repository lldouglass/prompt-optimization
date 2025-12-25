import { useState, useEffect, useRef } from "react"
import { useLocation } from "react-router-dom"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { FeedbackForm } from "@/components/FeedbackForm"
import { agentApi, sessionApi } from "@/lib/api"
import type { Judgment, CompareResult, OptimizationResult } from "@/lib/api"
import { track } from "@/lib/analytics"
import { CheckCircle, XCircle, Loader2, Scale, Gavel, Sparkles, ArrowRight, Save, AlertCircle, Lightbulb, ChevronDown, ChevronUp, Search, AlertTriangle, ShieldCheck, HelpCircle } from "lucide-react"

type TabMode = "evaluate" | "compare" | "optimize"

interface LocationState {
  autoEvaluate?: boolean
  request?: string
  response?: string
}

export function AgentsPage() {
  const location = useLocation()
  const state = location.state as LocationState | null
  const hasAutoRun = useRef(false)
  const optimizeResultsRef = useRef<HTMLDivElement>(null)

  const [activeTab, setActiveTab] = useState<TabMode>(state?.autoEvaluate ? "evaluate" : "optimize")

  // Standalone evaluate state - initialize from navigation state if present
  const [evalRequest, setEvalRequest] = useState(state?.request || "")
  const [evalResponse, setEvalResponse] = useState(state?.response || "")
  const [evalRubric, setEvalRubric] = useState("")
  const [evalJudgment, setEvalJudgment] = useState<Judgment | null>(null)
  const [evalLoading, setEvalLoading] = useState(false)
  const [evalSaveLoading, setEvalSaveLoading] = useState(false)
  const [evalSaved, setEvalSaved] = useState(false)

  // Compare state
  const [compareRequest, setCompareRequest] = useState("")
  const [compareResponseA, setCompareResponseA] = useState("")
  const [compareResponseB, setCompareResponseB] = useState("")
  const [compareModelA, setCompareModelA] = useState("")
  const [compareModelB, setCompareModelB] = useState("")
  const [compareRubric, setCompareRubric] = useState("")
  const [compareResult, setCompareResult] = useState<CompareResult | null>(null)
  const [compareLoading, setCompareLoading] = useState(false)
  const [compareSaveLoading, setCompareSaveLoading] = useState(false)
  const [compareSaved, setCompareSaved] = useState(false)

  const modelOptions = [
    { value: "", label: "Select model..." },
    { value: "gpt-5.2-pro", label: "GPT-5.2 Pro" },
    { value: "gpt-5.2-thinking", label: "GPT-5.2 Thinking" },
    { value: "gpt-5.2-instant", label: "GPT-5.2 Instant" },
    { value: "claude-opus-4.5", label: "Claude Opus 4.5" },
    { value: "claude-sonnet-4", label: "Claude Sonnet 4" },
    { value: "claude-haiku-4", label: "Claude Haiku 4" },
    { value: "gemini-3-pro", label: "Gemini 3 Pro" },
    { value: "gemini-3-flash", label: "Gemini 3 Flash" },
    { value: "gemini-3-deep-think", label: "Gemini 3 Deep Think" },
    { value: "grok-4.1", label: "Grok 4.1" },
    { value: "llama-3.3-70b", label: "Llama 3.3 70B" },
    { value: "mistral-large-2", label: "Mistral Large 2" },
    { value: "other", label: "Other" },
  ]

  // Optimize state
  const [optimizePrompt, setOptimizePrompt] = useState("")
  const [optimizeTask, setOptimizeTask] = useState("")
  const [optimizeSamples, setOptimizeSamples] = useState("")
  const [optimizeResult, setOptimizeResult] = useState<OptimizationResult | null>(null)
  const [optimizeLoading, setOptimizeLoading] = useState(false)
  const [optimizeError, setOptimizeError] = useState<string | null>(null)
  const [saveLoading, setSaveLoading] = useState(false)
  const [saved, setSaved] = useState(false)
  const [expandedExamples, setExpandedExamples] = useState<Set<number>>(new Set())

  const toggleExample = (index: number) => {
    setExpandedExamples(prev => {
      const newSet = new Set(prev)
      if (newSet.has(index)) {
        newSet.delete(index)
      } else {
        newSet.add(index)
      }
      return newSet
    })
  }

  const runEvaluate = async (request?: string, response?: string) => {
    const reqText = request ?? evalRequest
    const resText = response ?? evalResponse
    if (!reqText.trim() || !resText.trim()) return

    setEvalLoading(true)
    setEvalJudgment(null)
    setEvalSaved(false)

    try {
      const result = await agentApi.evaluate(
        reqText,
        resText,
        evalRubric || undefined
      )
      setEvalJudgment(result)
    } catch (error) {
      console.error("Evaluate error:", error)
    } finally {
      setEvalLoading(false)
    }
  }

  // Auto-run evaluation when navigated from Dashboard
  useEffect(() => {
    if (state?.autoEvaluate && state.request && state.response && !hasAutoRun.current) {
      hasAutoRun.current = true
      // Small delay to ensure state is set
      setTimeout(() => {
        runEvaluate(state.request, state.response)
      }, 100)
    }
  }, [state])

  const runCompare = async () => {
    if (!compareRequest.trim() || !compareResponseA.trim() || !compareResponseB.trim()) return

    setCompareLoading(true)
    setCompareResult(null)
    setCompareSaved(false)

    try {
      const result = await agentApi.compare(
        compareRequest,
        compareResponseA,
        compareResponseB,
        compareRubric || undefined
      )
      setCompareResult(result)
    } catch (error) {
      console.error("Compare error:", error)
    } finally {
      setCompareLoading(false)
    }
  }

  const saveEvaluation = async () => {
    if (!evalJudgment) return

    setEvalSaveLoading(true)
    try {
      await sessionApi.saveEvaluation(evalRequest, evalResponse, evalJudgment)
      setEvalSaved(true)
    } catch (error) {
      console.error("Save evaluation error:", error)
    } finally {
      setEvalSaveLoading(false)
    }
  }

  const saveComparison = async () => {
    if (!compareResult) return

    setCompareSaveLoading(true)
    try {
      await sessionApi.saveComparison(
        compareRequest,
        compareResponseA,
        compareResponseB,
        compareResult,
        compareModelA || undefined,
        compareModelB || undefined
      )
      setCompareSaved(true)
    } catch (error) {
      console.error("Save comparison error:", error)
    } finally {
      setCompareSaveLoading(false)
    }
  }

  const runOptimize = async () => {
    if (!optimizePrompt.trim() || !optimizeTask.trim()) return

    setOptimizeLoading(true)
    setOptimizeResult(null)
    setOptimizeError(null)
    setSaved(false)
    setExpandedExamples(new Set())

    // Track optimization started
    track('optimization_started', {
      prompt_length: optimizePrompt.length,
      task_length: optimizeTask.length,
    })

    try {
      // Parse sample inputs (one per line)
      const sampleInputs = optimizeSamples
        .split("\n")
        .map((s) => s.trim())
        .filter((s) => s.length > 0)

      const result = await sessionApi.optimize(
        optimizePrompt,
        optimizeTask,
        sampleInputs.length > 0 ? sampleInputs : undefined
      )
      setOptimizeResult(result)

      // Auto-scroll to results
      setTimeout(() => {
        optimizeResultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" })
      }, 100)

      // Track optimization completed with scores
      track('optimization_completed', {
        original_score: result.original_score,
        optimized_score: result.optimized_score,
        score_improvement: result.optimized_score - result.original_score,
        improvements_count: result.improvements?.length || 0,
      })
    } catch (error) {
      console.error("Optimize error:", error)
      track('optimization_failed', {
        error: error instanceof Error ? error.message : 'Unknown error',
      })
      if (error instanceof Error) {
        setOptimizeError(error.message)
      } else {
        setOptimizeError("Failed to optimize prompt")
      }
    } finally {
      setOptimizeLoading(false)
    }
  }

  const saveOptimization = async () => {
    if (!optimizeResult) return

    setSaveLoading(true)
    try {
      await sessionApi.saveOptimization(optimizeResult, optimizeTask)
      setSaved(true)
    } catch (error) {
      console.error("Save error:", error)
    } finally {
      setSaveLoading(false)
    }
  }

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Agent Tools</h1>
        <p className="text-muted-foreground mt-2">
          Evaluate, compare, and optimize prompts
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 border-b">
        <button
          onClick={() => setActiveTab("optimize")}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === "optimize"
              ? "border-b-2 border-primary text-primary"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          <Sparkles className="h-4 w-4 inline mr-2" />
          Optimize
        </button>
        <button
          onClick={() => setActiveTab("evaluate")}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === "evaluate"
              ? "border-b-2 border-primary text-primary"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          <Gavel className="h-4 w-4 inline mr-2" />
          Evaluate
        </button>
        <button
          onClick={() => setActiveTab("compare")}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === "compare"
              ? "border-b-2 border-primary text-primary"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          <Scale className="h-4 w-4 inline mr-2" />
          Compare
        </button>
      </div>

      {/* Evaluate Tab */}
      {activeTab === "evaluate" && (
        <>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Gavel className="h-5 w-5" />
                Judge Evaluator
              </CardTitle>
              <CardDescription>
                Evaluate a response against a request using the Judge agent
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium">Request / Prompt</label>
                <textarea
                  className="w-full min-h-[80px] p-3 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary mt-1"
                  placeholder="The original request or prompt..."
                  value={evalRequest}
                  onChange={(e) => setEvalRequest(e.target.value)}
                />
              </div>
              <div>
                <label className="text-sm font-medium">Response to Evaluate</label>
                <textarea
                  className="w-full min-h-[120px] p-3 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary mt-1"
                  placeholder="The response to evaluate..."
                  value={evalResponse}
                  onChange={(e) => setEvalResponse(e.target.value)}
                />
              </div>
              <div>
                <label className="text-sm font-medium">Custom Rubric (optional)</label>
                <textarea
                  className="w-full min-h-[60px] p-3 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary mt-1"
                  placeholder="Custom evaluation criteria... (leave empty for default)"
                  value={evalRubric}
                  onChange={(e) => setEvalRubric(e.target.value)}
                />
              </div>
              <Button
                onClick={() => runEvaluate()}
                disabled={evalLoading || !evalRequest.trim() || !evalResponse.trim()}
              >
                {evalLoading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Evaluating...
                  </>
                ) : (
                  <>
                    <Gavel className="h-4 w-4 mr-2" />
                    Evaluate Response
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {evalJudgment && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {evalJudgment.passed ? (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-500" />
                  )}
                  Evaluation Result
                </CardTitle>
                <CardDescription>
                  Overall Score: {evalJudgment.overall_score}/5 |{" "}
                  {evalJudgment.passed ? "Passed" : "Failed"}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {Object.keys(evalJudgment.scores).length > 0 && (
                  <div>
                    <div className="text-sm font-medium text-muted-foreground">Scores</div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-1">
                      {Object.entries(evalJudgment.scores).map(([criterion, score]) => (
                        <div key={criterion} className="p-2 bg-muted rounded">
                          <div className="text-xs text-muted-foreground capitalize">
                            {criterion}
                          </div>
                          <div className="font-medium">{score}/5</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                {evalJudgment.strengths.length > 0 && (
                  <div>
                    <div className="text-sm font-medium text-green-600">Strengths</div>
                    <ul className="list-disc list-inside mt-1 text-sm">
                      {evalJudgment.strengths.map((s, i) => (
                        <li key={i}>{s}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {evalJudgment.weaknesses.length > 0 && (
                  <div>
                    <div className="text-sm font-medium text-red-600">Weaknesses</div>
                    <ul className="list-disc list-inside mt-1 text-sm">
                      {evalJudgment.weaknesses.map((w, i) => (
                        <li key={i}>{w}</li>
                      ))}
                    </ul>
                  </div>
                )}
                <div>
                  <div className="text-sm font-medium text-muted-foreground">Reasoning</div>
                  <div className="mt-1 text-sm">{evalJudgment.reasoning}</div>
                </div>

                {/* Hallucination Check Results */}
                {evalJudgment.hallucination_check && (
                  <div className="border-t pt-4">
                    <div className="flex items-center gap-2 mb-3">
                      <Search className="h-4 w-4" />
                      <span className="text-sm font-medium">Fact Check Results</span>
                      {evalJudgment.hallucination_check.has_hallucinations ? (
                        <Badge variant="destructive" className="ml-auto">
                          <AlertTriangle className="h-3 w-3 mr-1" />
                          Potential Hallucinations
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="ml-auto text-green-600 border-green-600">
                          <ShieldCheck className="h-3 w-3 mr-1" />
                          Claims Verified
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground mb-3">
                      {evalJudgment.hallucination_check.summary}
                    </p>

                    {evalJudgment.hallucination_check.contradicted_claims.length > 0 && (
                      <div className="mb-3">
                        <div className="text-sm font-medium text-red-600 mb-2 flex items-center gap-1">
                          <XCircle className="h-4 w-4" /> Contradicted Claims
                        </div>
                        <div className="space-y-2">
                          {evalJudgment.hallucination_check.contradicted_claims.map((claim, i) => (
                            <div key={i} className="p-2 bg-red-50 dark:bg-red-950/20 rounded border border-red-200 dark:border-red-800 text-sm">
                              <div className="font-medium">{claim.claim}</div>
                              <div className="text-muted-foreground mt-1">{claim.evidence}</div>
                              {claim.source && (
                                <a href={claim.source} target="_blank" rel="noopener noreferrer" className="text-blue-600 text-xs hover:underline mt-1 block">
                                  Source
                                </a>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {evalJudgment.hallucination_check.verified_claims.length > 0 && (
                      <div className="mb-3">
                        <div className="text-sm font-medium text-green-600 mb-2 flex items-center gap-1">
                          <CheckCircle className="h-4 w-4" /> Verified Claims
                        </div>
                        <div className="space-y-2">
                          {evalJudgment.hallucination_check.verified_claims.map((claim, i) => (
                            <div key={i} className="p-2 bg-green-50 dark:bg-green-950/20 rounded border border-green-200 dark:border-green-800 text-sm">
                              <div className="font-medium">{claim.claim}</div>
                              <div className="text-muted-foreground mt-1">{claim.evidence}</div>
                              {claim.source && (
                                <a href={claim.source} target="_blank" rel="noopener noreferrer" className="text-blue-600 text-xs hover:underline mt-1 block">
                                  Source
                                </a>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {evalJudgment.hallucination_check.unverified_claims.length > 0 && (
                      <div>
                        <div className="text-sm font-medium text-yellow-600 mb-2 flex items-center gap-1">
                          <HelpCircle className="h-4 w-4" /> Unverified Claims
                        </div>
                        <div className="space-y-2">
                          {evalJudgment.hallucination_check.unverified_claims.map((claim, i) => (
                            <div key={i} className="p-2 bg-yellow-50 dark:bg-yellow-950/20 rounded border border-yellow-200 dark:border-yellow-800 text-sm">
                              <div className="font-medium">{claim.claim}</div>
                              <div className="text-muted-foreground mt-1">{claim.evidence}</div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Save Button */}
                <div className="border-t pt-4 flex justify-end">
                  <Button
                    onClick={saveEvaluation}
                    disabled={evalSaveLoading || evalSaved}
                  >
                    {evalSaveLoading ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Saving...
                      </>
                    ) : evalSaved ? (
                      <>
                        <CheckCircle className="h-4 w-4 mr-2" />
                        Saved to Library
                      </>
                    ) : (
                      <>
                        <Save className="h-4 w-4 mr-2" />
                        Save to Library
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Feedback Form */}
          {evalJudgment && (
            <FeedbackForm
              feedbackType="evaluation"
              contextSnapshot={{
                request: evalRequest,
                response: evalResponse,
                rubric: evalRubric,
                judgment: evalJudgment,
              }}
            />
          )}
        </>
      )}

      {/* Compare Tab */}
      {activeTab === "compare" && (
        <>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Scale className="h-5 w-5" />
                Compare Responses
              </CardTitle>
              <CardDescription>
                Compare two responses to determine which is better
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium">Request / Prompt</label>
                <textarea
                  className="w-full min-h-[80px] p-3 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary mt-1"
                  placeholder="The original request or prompt..."
                  value={compareRequest}
                  onChange={(e) => setCompareRequest(e.target.value)}
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <label className="text-sm font-medium">Response A</label>
                    <select
                      className="text-sm border rounded-md px-2 py-1 bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                      value={compareModelA}
                      onChange={(e) => setCompareModelA(e.target.value)}
                    >
                      {modelOptions.map((opt) => (
                        <option key={opt.value} value={opt.value}>
                          {opt.label}
                        </option>
                      ))}
                    </select>
                  </div>
                  <textarea
                    className="w-full min-h-[150px] p-3 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="Paste the first response..."
                    value={compareResponseA}
                    onChange={(e) => setCompareResponseA(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <label className="text-sm font-medium">Response B</label>
                    <select
                      className="text-sm border rounded-md px-2 py-1 bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                      value={compareModelB}
                      onChange={(e) => setCompareModelB(e.target.value)}
                    >
                      {modelOptions.map((opt) => (
                        <option key={opt.value} value={opt.value}>
                          {opt.label}
                        </option>
                      ))}
                    </select>
                  </div>
                  <textarea
                    className="w-full min-h-[150px] p-3 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="Paste the second response..."
                    value={compareResponseB}
                    onChange={(e) => setCompareResponseB(e.target.value)}
                  />
                </div>
              </div>
              <div>
                <label className="text-sm font-medium">Custom Rubric (optional)</label>
                <textarea
                  className="w-full min-h-[60px] p-3 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary mt-1"
                  placeholder="Custom comparison criteria... (leave empty for default)"
                  value={compareRubric}
                  onChange={(e) => setCompareRubric(e.target.value)}
                />
              </div>
              <Button
                onClick={runCompare}
                disabled={
                  compareLoading ||
                  !compareRequest.trim() ||
                  !compareResponseA.trim() ||
                  !compareResponseB.trim()
                }
              >
                {compareLoading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Comparing...
                  </>
                ) : (
                  <>
                    <Scale className="h-4 w-4 mr-2" />
                    Compare Responses
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {compareResult && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Scale className="h-5 w-5" />
                  Comparison Result
                </CardTitle>
                <CardDescription>
                  Winner:{" "}
                  <span className="font-bold">
                    {compareResult.winner === "A"
                      ? compareModelA || "Response A"
                      : compareResult.winner === "B"
                      ? compareModelB || "Response B"
                      : "Tie"}
                  </span>{" "}
                  | Confidence: {compareResult.confidence}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {Object.keys(compareResult.comparison).length > 0 && (
                  <div>
                    <div className="text-sm font-medium text-muted-foreground">
                      Criterion Breakdown
                    </div>
                    <div className="space-y-2 mt-2">
                      {Object.entries(compareResult.comparison).map(([criterion, details]) => (
                        <div key={criterion} className="p-3 bg-muted rounded-lg">
                          <div className="flex justify-between items-center">
                            <span className="font-medium capitalize">{criterion}</span>
                            <Badge
                              variant={details.winner === "A" ? "default" : "secondary"}
                            >
                              {details.winner === "A"
                                ? compareModelA || "Response A"
                                : details.winner === "B"
                                ? compareModelB || "Response B"
                                : "Tie"}
                            </Badge>
                          </div>
                          <div className="text-sm text-muted-foreground mt-1">
                            {details.explanation}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                <div>
                  <div className="text-sm font-medium text-muted-foreground">Reasoning</div>
                  <div className="mt-1 text-sm">{compareResult.reasoning}</div>
                </div>

                {/* Hallucination Check Results for Both Responses */}
                {(compareResult.hallucination_check_a || compareResult.hallucination_check_b) && (
                  <div className="border-t pt-4">
                    <div className="flex items-center gap-2 mb-4">
                      <Search className="h-4 w-4" />
                      <span className="text-sm font-medium">Fact Check Results</span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {/* Response A Hallucination Check */}
                      {compareResult.hallucination_check_a && (
                        <div className="p-3 border rounded-lg">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="font-medium text-sm">{compareModelA || "Response A"}</span>
                            {compareResult.hallucination_check_a.has_hallucinations ? (
                              <Badge variant="destructive" className="text-xs">
                                <AlertTriangle className="h-3 w-3 mr-1" />
                                Issues Found
                              </Badge>
                            ) : (
                              <Badge variant="outline" className="text-xs text-green-600 border-green-600">
                                <ShieldCheck className="h-3 w-3 mr-1" />
                                Verified
                              </Badge>
                            )}
                          </div>
                          <p className="text-xs text-muted-foreground">
                            {compareResult.hallucination_check_a.summary}
                          </p>
                          {compareResult.hallucination_check_a.contradicted_claims.length > 0 && (
                            <div className="mt-2 space-y-1">
                              {compareResult.hallucination_check_a.contradicted_claims.map((claim, i) => (
                                <div key={i} className="text-xs p-1.5 bg-red-50 dark:bg-red-950/20 rounded text-red-700 dark:text-red-300">
                                  {claim.claim}
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )}

                      {/* Response B Hallucination Check */}
                      {compareResult.hallucination_check_b && (
                        <div className="p-3 border rounded-lg">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="font-medium text-sm">{compareModelB || "Response B"}</span>
                            {compareResult.hallucination_check_b.has_hallucinations ? (
                              <Badge variant="destructive" className="text-xs">
                                <AlertTriangle className="h-3 w-3 mr-1" />
                                Issues Found
                              </Badge>
                            ) : (
                              <Badge variant="outline" className="text-xs text-green-600 border-green-600">
                                <ShieldCheck className="h-3 w-3 mr-1" />
                                Verified
                              </Badge>
                            )}
                          </div>
                          <p className="text-xs text-muted-foreground">
                            {compareResult.hallucination_check_b.summary}
                          </p>
                          {compareResult.hallucination_check_b.contradicted_claims.length > 0 && (
                            <div className="mt-2 space-y-1">
                              {compareResult.hallucination_check_b.contradicted_claims.map((claim, i) => (
                                <div key={i} className="text-xs p-1.5 bg-red-50 dark:bg-red-950/20 rounded text-red-700 dark:text-red-300">
                                  {claim.claim}
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Save Button */}
                <div className="border-t pt-4 flex justify-end">
                  <Button
                    onClick={saveComparison}
                    disabled={compareSaveLoading || compareSaved}
                  >
                    {compareSaveLoading ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Saving...
                      </>
                    ) : compareSaved ? (
                      <>
                        <CheckCircle className="h-4 w-4 mr-2" />
                        Saved to Library
                      </>
                    ) : (
                      <>
                        <Save className="h-4 w-4 mr-2" />
                        Save to Library
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Feedback Form */}
          {compareResult && (
            <FeedbackForm
              feedbackType="comparison"
              contextSnapshot={{
                request: compareRequest,
                responseA: compareResponseA,
                responseB: compareResponseB,
                modelA: compareModelA,
                modelB: compareModelB,
                rubric: compareRubric,
                result: compareResult,
              }}
            />
          )}
        </>
      )}

      {/* Optimize Tab */}
      {activeTab === "optimize" && (
        <>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5" />
                Prompt Optimizer
              </CardTitle>
              <CardDescription>
                Analyze and optimize prompts using AI-powered best practices
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium">Your Current Prompt</label>
                <textarea
                  className="w-full min-h-[150px] p-3 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary mt-1 font-mono text-sm"
                  placeholder="Paste the prompt you want to improve..."
                  value={optimizePrompt}
                  onChange={(e) => setOptimizePrompt(e.target.value)}
                />
              </div>

              <div>
                <label className="text-sm font-medium">What should this prompt do?</label>
                <textarea
                  className="w-full min-h-[80px] p-3 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary mt-1"
                  placeholder="e.g., Summarize articles, Write marketing copy, Answer customer questions..."
                  value={optimizeTask}
                  onChange={(e) => setOptimizeTask(e.target.value)}
                />
              </div>

              <div>
                <label className="text-sm font-medium">Example inputs (optional)</label>
                <textarea
                  className="w-full min-h-[80px] p-3 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary mt-1"
                  placeholder="Add a few examples of what users might ask, one per line..."
                  value={optimizeSamples}
                  onChange={(e) => setOptimizeSamples(e.target.value)}
                />
              </div>

              <Button
                onClick={runOptimize}
                disabled={optimizeLoading || !optimizePrompt.trim() || !optimizeTask.trim()}
              >
                {optimizeLoading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Optimizing...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4 mr-2" />
                    Optimize Prompt
                  </>
                )}
              </Button>

              {optimizeError && (
                <div className="flex items-start gap-2 p-3 bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-800 rounded-lg">
                  <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
                  <div className="text-sm text-red-800 dark:text-red-200">
                    {optimizeError}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {optimizeResult && (
            <div ref={optimizeResultsRef}>
              {/* Score Comparison */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <ArrowRight className="h-5 w-5" />
                    Optimization Results
                  </CardTitle>
                  <CardDescription>
                    Score improved from {optimizeResult.original_score.toFixed(1)} to{" "}
                    {optimizeResult.optimized_score.toFixed(1)}
                    {optimizeResult.optimized_score > optimizeResult.original_score && (
                      <span className="text-green-600 ml-2">
                        (+{(optimizeResult.optimized_score - optimizeResult.original_score).toFixed(1)})
                      </span>
                    )}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Score bars */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-sm font-medium mb-1">Original Score</div>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-muted rounded-full h-3">
                          <div
                            className="bg-orange-500 h-3 rounded-full"
                            style={{ width: `${(optimizeResult.original_score / 10) * 100}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium w-10">
                          {optimizeResult.original_score.toFixed(1)}
                        </span>
                      </div>
                    </div>
                    <div>
                      <div className="text-sm font-medium mb-1">Optimized Score</div>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-muted rounded-full h-3">
                          <div
                            className="bg-green-500 h-3 rounded-full"
                            style={{ width: `${(optimizeResult.optimized_score / 10) * 100}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium w-10">
                          {optimizeResult.optimized_score.toFixed(1)}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Improvements list */}
                  {optimizeResult.improvements.length > 0 && (
                    <div>
                      <div className="text-sm font-medium text-muted-foreground mb-2">
                        Improvements Made
                      </div>
                      <ul className="space-y-1">
                        {optimizeResult.improvements.map((improvement, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm">
                            <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                            {improvement}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Reasoning */}
                  <div>
                    <div className="text-sm font-medium text-muted-foreground">Reasoning</div>
                    <div className="mt-1 text-sm">{optimizeResult.reasoning}</div>
                  </div>
                </CardContent>
              </Card>

              {/* Side-by-side prompts */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base flex items-center gap-2">
                      <XCircle className="h-4 w-4 text-orange-500" />
                      Original Prompt
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="bg-muted p-4 rounded-lg whitespace-pre-wrap font-mono text-sm max-h-96 overflow-auto">
                      {optimizeResult.original_prompt}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      Optimized Prompt
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="bg-muted p-4 rounded-lg whitespace-pre-wrap font-mono text-sm max-h-96 overflow-auto">
                      {optimizeResult.optimized_prompt}
                    </div>
                    <div className="flex gap-2 mt-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          navigator.clipboard.writeText(optimizeResult.optimized_prompt)
                          track('prompt_copied', {
                            optimized_score: optimizeResult.optimized_score,
                          })
                        }}
                      >
                        Copy to Clipboard
                      </Button>
                      <Button
                        size="sm"
                        onClick={saveOptimization}
                        disabled={saveLoading || saved}
                      >
                        {saveLoading ? (
                          <>
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                            Saving...
                          </>
                        ) : saved ? (
                          <>
                            <CheckCircle className="h-4 w-4 mr-2" />
                            Saved
                          </>
                        ) : (
                          <>
                            <Save className="h-4 w-4 mr-2" />
                            Save to Library
                          </>
                        )}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Analysis details */}
              {optimizeResult.analysis && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Analysis Details</CardTitle>
                    <CardDescription>
                      Overall Quality: {optimizeResult.analysis.overall_quality}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {optimizeResult.analysis.issues.length > 0 && (
                      <div>
                        <div className="text-sm font-medium text-red-600 mb-2">Issues Found</div>
                        <div className="space-y-2">
                          {optimizeResult.analysis.issues.map((issue, i) => (
                            <div key={i} className="p-2 bg-red-50 dark:bg-red-950/20 rounded border border-red-200 dark:border-red-800">
                              <div className="flex items-center gap-2">
                                <Badge variant="outline" className="text-xs">
                                  {issue.category}
                                </Badge>
                                <Badge
                                  variant={
                                    issue.severity === "high"
                                      ? "destructive"
                                      : issue.severity === "medium"
                                      ? "default"
                                      : "secondary"
                                  }
                                  className="text-xs"
                                >
                                  {issue.severity}
                                </Badge>
                              </div>
                              <div className="text-sm mt-1">{issue.description}</div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {optimizeResult.analysis.strengths.length > 0 && (
                      <div>
                        <div className="text-sm font-medium text-green-600 mb-2">Strengths</div>
                        <ul className="list-disc list-inside text-sm space-y-1">
                          {optimizeResult.analysis.strengths.map((s, i) => (
                            <li key={i}>{s}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              {/* Few-Shot Research */}
              {optimizeResult.few_shot_research && optimizeResult.few_shot_research.examples.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base flex items-center gap-2">
                      <Lightbulb className="h-4 w-4 text-yellow-500" />
                      Generated Few-Shot Examples
                    </CardTitle>
                    <CardDescription>
                      {optimizeResult.few_shot_research.examples.length} examples researched and added to the optimized prompt
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {optimizeResult.few_shot_research.research_notes && (
                      <div className="p-3 bg-muted rounded-lg">
                        <div className="text-sm font-medium text-muted-foreground mb-1">Research Notes</div>
                        <div className="text-sm">{optimizeResult.few_shot_research.research_notes}</div>
                      </div>
                    )}

                    {optimizeResult.few_shot_research.format_recommendation && (
                      <div className="text-sm">
                        <span className="font-medium">Format: </span>
                        <code className="px-1.5 py-0.5 bg-muted rounded text-xs">
                          {optimizeResult.few_shot_research.format_recommendation}
                        </code>
                      </div>
                    )}

                    <div className="space-y-3">
                      {optimizeResult.few_shot_research.examples.map((example, i) => (
                        <div key={i} className="border rounded-lg overflow-hidden">
                          <button
                            onClick={() => toggleExample(i)}
                            className="w-full flex items-center justify-between p-3 hover:bg-muted/50 transition-colors text-left"
                          >
                            <div className="flex items-center gap-2">
                              <Badge variant="outline" className="text-xs">
                                Example {i + 1}
                              </Badge>
                              <span className="text-sm text-muted-foreground truncate max-w-md">
                                {example.input.substring(0, 60)}...
                              </span>
                            </div>
                            {expandedExamples.has(i) ? (
                              <ChevronUp className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                            ) : (
                              <ChevronDown className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                            )}
                          </button>

                          {expandedExamples.has(i) && (
                            <div className="p-3 border-t space-y-3">
                              <div>
                                <div className="text-xs font-medium text-muted-foreground mb-1">Input</div>
                                <div className="bg-muted p-2 rounded text-sm font-mono whitespace-pre-wrap">
                                  {example.input}
                                </div>
                              </div>
                              <div>
                                <div className="text-xs font-medium text-muted-foreground mb-1">Output</div>
                                <div className="bg-muted p-2 rounded text-sm font-mono whitespace-pre-wrap max-h-64 overflow-auto">
                                  {example.output}
                                </div>
                              </div>
                              {example.rationale && (
                                <div>
                                  <div className="text-xs font-medium text-muted-foreground mb-1">Rationale</div>
                                  <div className="text-sm italic text-muted-foreground">
                                    {example.rationale}
                                  </div>
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}
