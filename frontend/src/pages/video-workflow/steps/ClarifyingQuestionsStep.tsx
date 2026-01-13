import { useState, useEffect } from "react"
import { Loader2, MessageSquare, Sparkles } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { videoWorkflowApi, type VideoWorkflowDetail } from "@/lib/api"
import type { ClarifyingQuestion } from "@/types/video-workflow"

interface ClarifyingQuestionsStepProps {
  workflow: VideoWorkflowDetail | null
  onComplete: () => void
  onRefresh: () => void
}

export function ClarifyingQuestionsStep({ workflow, onComplete, onRefresh }: ClarifyingQuestionsStepProps) {
  const [isGenerating, setIsGenerating] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [questions, setQuestions] = useState<ClarifyingQuestion[]>([])
  const [answers, setAnswers] = useState<Record<string, string>>({})

  // Load existing questions from workflow, or auto-generate if none exist
  useEffect(() => {
    if (workflow?.brief?.clarifying_questions && workflow.brief.clarifying_questions.length > 0) {
      setQuestions(workflow.brief.clarifying_questions)
      // Pre-fill answers
      const existingAnswers: Record<string, string> = {}
      workflow.brief.clarifying_questions.forEach(q => {
        if (q.answer) {
          existingAnswers[q.id] = q.answer
        }
      })
      setAnswers(existingAnswers)
    } else if (workflow?.brief && !isGenerating && questions.length === 0) {
      // Auto-generate questions if brief exists but no questions yet
      handleGenerateQuestions()
    }
  }, [workflow])

  const handleGenerateQuestions = async () => {
    if (!workflow) return

    setIsGenerating(true)
    setError(null)

    try {
      const result = await videoWorkflowApi.generateQuestions(workflow.id)
      setQuestions(result.questions)
      onRefresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate questions")
    } finally {
      setIsGenerating(false)
    }
  }

  const handleSubmitAnswers = async () => {
    if (!workflow) return

    // Check that all questions have answers
    const unanswered = questions.filter(q => !answers[q.id]?.trim())
    if (unanswered.length > 0) {
      setError(`Please answer all questions (${unanswered.length} remaining)`)
      return
    }

    setIsSubmitting(true)
    setError(null)

    try {
      await videoWorkflowApi.submitAnswers(workflow.id, answers)
      onComplete()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to submit answers")
    } finally {
      setIsSubmitting(false)
    }
  }

  const getCategoryLabel = (category: string) => {
    const labels: Record<string, string> = {
      shot_style: "Shot Style",
      pacing: "Pacing",
      camera_movement: "Camera Movement",
      action_beats: "Action Beats",
      audio: "Audio",
      cta: "Call to Action",
    }
    return labels[category] || category
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MessageSquare className="h-5 w-5" />
          Clarifying Questions
        </CardTitle>
        <CardDescription>
          Answer these questions to help us create better prompts. AI will generate targeted questions based on your brief.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Generate Questions Button */}
        {questions.length === 0 && (
          <div className="text-center py-8 space-y-4">
            <p className="text-muted-foreground">
              Generate AI-powered questions based on your brief to fill in any gaps.
            </p>
            <Button onClick={handleGenerateQuestions} disabled={isGenerating}>
              {isGenerating ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Generating Questions...
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4 mr-2" />
                  Generate Questions
                </>
              )}
            </Button>
          </div>
        )}

        {/* Questions List */}
        {questions.length > 0 && (
          <div className="space-y-6">
            {questions.map((question, index) => (
              <div key={question.id} className="space-y-2">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-medium text-muted-foreground uppercase">
                    {getCategoryLabel(question.category)}
                  </span>
                </div>
                <Label htmlFor={question.id} className="text-base">
                  {index + 1}. {question.question}
                </Label>
                <Input
                  id={question.id}
                  value={answers[question.id] || ""}
                  onChange={e => setAnswers(prev => ({ ...prev, [question.id]: e.target.value }))}
                  placeholder="Your answer..."
                />
              </div>
            ))}

            {/* Regenerate Button */}
            <Button
              variant="outline"
              onClick={handleGenerateQuestions}
              disabled={isGenerating}
              className="mt-4"
            >
              {isGenerating ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Sparkles className="h-4 w-4 mr-2" />
              )}
              Regenerate Questions
            </Button>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="bg-destructive/10 text-destructive rounded-lg p-4">
            {error}
          </div>
        )}

        {/* Submit Button */}
        {questions.length > 0 && (
          <div className="flex justify-end">
            <Button onClick={handleSubmitAnswers} disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                "Save Answers & Continue"
              )}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
