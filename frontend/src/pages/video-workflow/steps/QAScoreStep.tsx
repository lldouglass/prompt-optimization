import { useState, useEffect } from "react"
import { Loader2, CheckCircle, AlertTriangle, XCircle, Sparkles, HelpCircle } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { videoWorkflowApi, type VideoWorkflowDetail } from "@/lib/api"
import type { QAScore } from "@/types/video-workflow"
import { ScoreCard } from "../components/ScoreGauge"

interface QAScoreStepProps {
  workflow: VideoWorkflowDetail | null
  onComplete: () => void
  onRefresh: () => void
}

export function QAScoreStep({ workflow, onComplete, onRefresh }: QAScoreStepProps) {
  const [isScoring, setIsScoring] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [qaScore, setQAScore] = useState<QAScore | null>(null)

  // Load existing QA score
  useEffect(() => {
    if (workflow?.qa_score) {
      setQAScore(workflow.qa_score)
    }
  }, [workflow])

  const handleRunQA = async () => {
    if (!workflow) return

    setIsScoring(true)
    setError(null)

    try {
      const result = await videoWorkflowApi.runQA(workflow.id)
      setQAScore(result.qa_score)
      onRefresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to run QA scoring")
    } finally {
      setIsScoring(false)
    }
  }

  const getScoreIcon = (score: number) => {
    if (score >= 70) return <CheckCircle className="h-5 w-5 text-green-600" />
    if (score >= 50) return <AlertTriangle className="h-5 w-5 text-yellow-600" />
    return <XCircle className="h-5 w-5 text-red-600" />
  }

  const getScoreLabel = (score: number) => {
    if (score >= 80) return "Excellent"
    if (score >= 70) return "Good"
    if (score >= 50) return "Needs Work"
    return "Poor"
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <CheckCircle className="h-5 w-5" />
          QA Score & Validation
        </CardTitle>
        <CardDescription>
          Analyze your workflow for potential issues before generating videos.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Run QA Button */}
        {!qaScore && (
          <div className="text-center py-8 space-y-4">
            <p className="text-muted-foreground">
              Run quality assurance checks on your prompts and shot plan.
            </p>
            <Button onClick={handleRunQA} disabled={isScoring}>
              {isScoring ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4 mr-2" />
                  Run QA Check
                </>
              )}
            </Button>
          </div>
        )}

        {/* QA Results */}
        {qaScore && (
          <>
            {/* Overall Score */}
            <div className="text-center p-6 bg-muted rounded-lg">
              <div className="flex items-center justify-center gap-2 mb-2">
                {getScoreIcon(qaScore.overall_score)}
                <span className="text-4xl font-bold">{qaScore.overall_score}</span>
                <span className="text-xl text-muted-foreground">/100</span>
              </div>
              <p className="text-lg font-medium">{getScoreLabel(qaScore.overall_score)}</p>
              <Button
                variant="outline"
                size="sm"
                onClick={handleRunQA}
                disabled={isScoring}
                className="mt-4"
              >
                {isScoring ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Sparkles className="h-4 w-4 mr-2" />
                )}
                Re-run QA
              </Button>
            </div>

            {/* Score Breakdown */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <ScoreCard
                score={qaScore.ambiguity_risk}
                label="Ambiguity Risk"
                description="Lower is better"
                inverted
              />
              <ScoreCard
                score={qaScore.motion_complexity_risk}
                label="Motion Complexity"
                description="Lower is better"
                inverted
              />
              <ScoreCard
                score={qaScore.continuity_completeness}
                label="Continuity"
                description="Higher is better"
              />
              <ScoreCard
                score={qaScore.audio_readiness}
                label="Audio Ready"
                description="Higher is better"
              />
            </div>

            {/* Warnings */}
            {qaScore.warnings.length > 0 && (
              <div className="space-y-3">
                <h3 className="font-medium flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-yellow-600" />
                  Warnings ({qaScore.warnings.length})
                </h3>
                <ul className="space-y-2">
                  {qaScore.warnings.map((warning, i) => (
                    <li
                      key={i}
                      className="flex items-start gap-2 p-3 bg-yellow-50 rounded-lg text-sm"
                    >
                      <AlertTriangle className="h-4 w-4 text-yellow-600 mt-0.5 flex-shrink-0" />
                      {warning}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Suggested Fixes */}
            {qaScore.fixes.length > 0 && (
              <div className="space-y-3">
                <h3 className="font-medium flex items-center gap-2">
                  <XCircle className="h-4 w-4 text-red-600" />
                  Suggested Fixes ({qaScore.fixes.length})
                </h3>
                <ul className="space-y-3">
                  {qaScore.fixes.map((fix, i) => (
                    <li key={i} className="p-3 bg-red-50 rounded-lg text-sm space-y-1">
                      <div className="font-medium text-red-900">{fix.issue}</div>
                      <div className="text-red-700">{fix.fix}</div>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Recommended Questions */}
            {qaScore.recommended_questions.length > 0 && (
              <div className="space-y-3">
                <h3 className="font-medium flex items-center gap-2">
                  <HelpCircle className="h-4 w-4 text-blue-600" />
                  Consider These Questions
                </h3>
                <ul className="space-y-2">
                  {qaScore.recommended_questions.map((question, i) => (
                    <li
                      key={i}
                      className="flex items-start gap-2 p-3 bg-blue-50 rounded-lg text-sm"
                    >
                      <HelpCircle className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                      {question}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* All Clear Message */}
            {qaScore.warnings.length === 0 && qaScore.fixes.length === 0 && (
              <div className="text-center p-6 bg-green-50 rounded-lg">
                <CheckCircle className="h-8 w-8 text-green-600 mx-auto mb-2" />
                <p className="font-medium text-green-900">All checks passed!</p>
                <p className="text-sm text-green-700">
                  Your workflow is ready for video generation.
                </p>
              </div>
            )}
          </>
        )}

        {/* Error Display */}
        {error && (
          <div className="bg-destructive/10 text-destructive rounded-lg p-4">
            {error}
          </div>
        )}

        {/* Continue Button */}
        {qaScore && (
          <div className="flex justify-end">
            <Button onClick={() => onComplete()}>
              Continue to Export
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
