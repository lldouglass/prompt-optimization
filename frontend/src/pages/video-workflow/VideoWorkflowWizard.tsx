import { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { ArrowLeft, ArrowRight, Loader2, Save } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { videoWorkflowApi, type VideoWorkflowDetail } from "@/lib/api"
import { track } from "@/lib/analytics"
import { WORKFLOW_STEPS } from "@/types/video-workflow"
import { WorkflowStepIndicator } from "./components/WorkflowStepIndicator"

// Step components
import { BriefIntakeStep } from "./steps/BriefIntakeStep"
import { ClarifyingQuestionsStep } from "./steps/ClarifyingQuestionsStep"
import { ContinuityPackStep } from "./steps/ContinuityPackStep"
import { ShotPlanStep } from "./steps/ShotPlanStep"
import { PromptPackStep } from "./steps/PromptPackStep"
import { QAScoreStep } from "./steps/QAScoreStep"
import { ExportStep } from "./steps/ExportStep"

export function VideoWorkflowWizard() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const [workflow, setWorkflow] = useState<VideoWorkflowDetail | null>(null)
  const [currentStep, setCurrentStep] = useState(1)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Load workflow on mount
  useEffect(() => {
    if (id && id !== "new") {
      loadWorkflow(id)
    } else {
      setIsLoading(false)
    }
  }, [id])

  const loadWorkflow = async (workflowId: string) => {
    setIsLoading(true)
    setError(null)
    try {
      const data = await videoWorkflowApi.get(workflowId)
      setWorkflow(data)
      setCurrentStep(data.current_step || 1)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load workflow")
    } finally {
      setIsLoading(false)
    }
  }

  const handleStepComplete = async () => {
    if (!workflow) return

    // Refresh workflow data
    await loadWorkflow(workflow.id)

    // Move to next step
    const nextStep = Math.min(currentStep + 1, 7)
    setCurrentStep(nextStep)

    track("video_workflow_step_completed", {
      workflow_id: workflow.id,
      step: currentStep,
      step_name: WORKFLOW_STEPS.find(s => s.number === currentStep)?.name,
    })
  }

  const handleBack = () => {
    setCurrentStep(Math.max(1, currentStep - 1))
  }

  const handleNext = () => {
    setCurrentStep(Math.min(7, currentStep + 1))
  }

  const handleStepClick = (step: number) => {
    if (step <= (workflow?.current_step || 1)) {
      setCurrentStep(step)
    }
  }

  const handleSaveVersion = async (step: "brief" | "continuity" | "shots" | "prompts") => {
    if (!workflow) return

    setIsSaving(true)
    try {
      await videoWorkflowApi.saveVersion(workflow.id, step)
      await loadWorkflow(workflow.id)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save version")
    } finally {
      setIsSaving(false)
    }
  }

  const renderStep = () => {
    if (!workflow && id !== "new") {
      return null
    }

    const refreshWorkflow = () => workflow && loadWorkflow(workflow.id)

    switch (currentStep) {
      case 1:
        return <BriefIntakeStep workflow={workflow} onComplete={handleStepComplete} />
      case 2:
        return <ClarifyingQuestionsStep workflow={workflow} onComplete={handleStepComplete} onRefresh={refreshWorkflow} />
      case 3:
        return <ContinuityPackStep workflow={workflow} onComplete={handleStepComplete} onRefresh={refreshWorkflow} />
      case 4:
        return <ShotPlanStep workflow={workflow} onComplete={handleStepComplete} onRefresh={refreshWorkflow} />
      case 5:
        return <PromptPackStep workflow={workflow} onComplete={handleStepComplete} onRefresh={refreshWorkflow} />
      case 6:
        return <QAScoreStep workflow={workflow} onComplete={handleStepComplete} onRefresh={refreshWorkflow} />
      case 7:
        return <ExportStep workflow={workflow} />
      default:
        return null
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="container max-w-5xl mx-auto py-6 px-4 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">
            {workflow?.name || "New Video Workflow"}
          </h1>
          <p className="text-muted-foreground">
            Create Sora 2 prompts from your video concept
          </p>
        </div>
        <Button variant="outline" onClick={() => navigate("/video-workflow")}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to List
        </Button>
      </div>

      {/* Step Indicator */}
      <Card>
        <CardContent className="pt-6">
          <WorkflowStepIndicator
            currentStep={currentStep}
            completedSteps={
              workflow
                ? Array.from({ length: workflow.current_step }, (_, i) => i + 1)
                : []
            }
            onStepClick={handleStepClick}
          />
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <div className="bg-destructive/10 text-destructive rounded-lg p-4">
          {error}
        </div>
      )}

      {/* Step Content */}
      <div className="min-h-[400px]">
        {renderStep()}
      </div>

      {/* Navigation */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <Button
              variant="outline"
              onClick={handleBack}
              disabled={currentStep === 1}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Previous
            </Button>

            <div className="flex items-center gap-2">
              {/* Save Version Button (for applicable steps) */}
              {workflow && currentStep >= 1 && currentStep <= 5 && (
                <Button
                  variant="outline"
                  onClick={() => {
                    const stepKey = ["brief", "brief", "continuity", "shots", "prompts"][currentStep - 1] as "brief" | "continuity" | "shots" | "prompts"
                    handleSaveVersion(stepKey)
                  }}
                  disabled={isSaving}
                >
                  {isSaving ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <Save className="h-4 w-4 mr-2" />
                  )}
                  Save Version
                </Button>
              )}
            </div>

            <Button
              onClick={handleNext}
              disabled={currentStep === 7 || !workflow || currentStep > (workflow.current_step || 0)}
            >
              Next
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
