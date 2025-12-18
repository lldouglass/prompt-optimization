import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import {
  ThumbsUp,
  ThumbsDown,
  MessageSquare,
  Loader2,
  CheckCircle,
  Star
} from "lucide-react"

interface FeedbackFormProps {
  feedbackType: "evaluation" | "comparison"
  contextSnapshot: Record<string, unknown>
  savedEvaluationId?: string
  onSubmitSuccess?: () => void
}

export function FeedbackForm({
  feedbackType,
  contextSnapshot,
  savedEvaluationId,
  onSubmitSuccess
}: FeedbackFormProps) {
  const [agreesWithResult, setAgreesWithResult] = useState<boolean | null>(null)
  const [qualityRating, setQualityRating] = useState<number | null>(null)
  const [comment, setComment] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async () => {
    if (agreesWithResult === null && qualityRating === null && !comment.trim()) {
      setError("Please provide at least one form of feedback")
      return
    }

    setIsSubmitting(true)
    setError(null)

    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || "http://localhost:8000"}/api/v1/agents/feedback`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({
            feedback_type: feedbackType,
            agrees_with_result: agreesWithResult,
            quality_rating: qualityRating,
            comment: comment.trim() || null,
            saved_evaluation_id: savedEvaluationId,
            context_snapshot: contextSnapshot,
          }),
        }
      )

      if (!response.ok) {
        throw new Error("Failed to submit feedback")
      }

      setIsSubmitted(true)
      onSubmitSuccess?.()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to submit feedback")
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isSubmitted) {
    return (
      <Card className="border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-950/20">
        <CardContent className="pt-6">
          <div className="flex items-center gap-2 text-green-600">
            <CheckCircle className="h-5 w-5" />
            <span className="font-medium">Thank you for your feedback!</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <MessageSquare className="h-4 w-4" />
          Provide Feedback
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Agreement Section */}
        <div>
          <label className="text-sm font-medium">
            Do you agree with this {feedbackType === "evaluation" ? "evaluation" : "comparison"} result?
          </label>
          <div className="flex gap-2 mt-2">
            <Button
              variant={agreesWithResult === true ? "default" : "outline"}
              size="sm"
              onClick={() => setAgreesWithResult(true)}
              className={agreesWithResult === true ? "bg-green-600 hover:bg-green-700" : ""}
            >
              <ThumbsUp className="h-4 w-4 mr-1" />
              Agree
            </Button>
            <Button
              variant={agreesWithResult === false ? "default" : "outline"}
              size="sm"
              onClick={() => setAgreesWithResult(false)}
              className={agreesWithResult === false ? "bg-red-600 hover:bg-red-700" : ""}
            >
              <ThumbsDown className="h-4 w-4 mr-1" />
              Disagree
            </Button>
            {agreesWithResult !== null && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setAgreesWithResult(null)}
                className="text-muted-foreground"
              >
                Clear
              </Button>
            )}
          </div>
        </div>

        {/* Quality Rating Section */}
        <div>
          <label className="text-sm font-medium">
            Rate the quality of this result (1-10)
          </label>
          <div className="flex gap-1 mt-2">
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((rating) => (
              <button
                key={rating}
                onClick={() => setQualityRating(qualityRating === rating ? null : rating)}
                className={`
                  w-8 h-8 rounded-md text-sm font-medium transition-colors
                  ${qualityRating === rating
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted hover:bg-muted/80 text-muted-foreground"
                  }
                `}
              >
                {rating}
              </button>
            ))}
          </div>
          {qualityRating !== null && (
            <div className="flex items-center gap-2 mt-1">
              <Star className="h-4 w-4 text-yellow-500" />
              <span className="text-sm text-muted-foreground">
                You rated this {qualityRating}/10
              </span>
            </div>
          )}
        </div>

        {/* Comment Section */}
        <div>
          <label className="text-sm font-medium">Additional comments (optional)</label>
          <textarea
            className="w-full min-h-[80px] p-3 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary mt-1 text-sm"
            placeholder="Share any additional thoughts about this result..."
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            maxLength={2000}
          />
          <div className="text-xs text-muted-foreground text-right">
            {comment.length}/2000
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="text-sm text-red-600">{error}</div>
        )}

        {/* Submit Button */}
        <Button
          onClick={handleSubmit}
          disabled={isSubmitting}
          className="w-full"
        >
          {isSubmitting ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Submitting...
            </>
          ) : (
            <>
              <MessageSquare className="h-4 w-4 mr-2" />
              Submit Feedback
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  )
}
