import { Check } from "lucide-react"
import { cn } from "@/lib/utils"
import { WORKFLOW_STEPS } from "@/types/video-workflow"

interface WorkflowStepIndicatorProps {
  currentStep: number
  onStepClick?: (step: number) => void
  completedSteps?: number[]
}

export function WorkflowStepIndicator({
  currentStep,
  onStepClick,
  completedSteps = [],
}: WorkflowStepIndicatorProps) {
  return (
    <div className="w-full">
      <div className="flex items-center justify-between">
        {WORKFLOW_STEPS.map((step, index) => {
          const isCompleted = completedSteps.includes(step.number) || step.number < currentStep
          const isCurrent = step.number === currentStep
          const isClickable = onStepClick && (isCompleted || step.number <= currentStep)

          return (
            <div key={step.number} className="flex items-center flex-1">
              {/* Step Circle */}
              <button
                onClick={() => isClickable && onStepClick?.(step.number)}
                disabled={!isClickable}
                className={cn(
                  "relative flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium transition-colors",
                  isCompleted && "bg-primary text-primary-foreground",
                  isCurrent && !isCompleted && "bg-primary/20 text-primary border-2 border-primary",
                  !isCompleted && !isCurrent && "bg-muted text-muted-foreground",
                  isClickable && "cursor-pointer hover:opacity-80",
                  !isClickable && "cursor-default"
                )}
              >
                {isCompleted ? (
                  <Check className="h-4 w-4" />
                ) : (
                  step.number
                )}
              </button>

              {/* Step Label (hidden on mobile) */}
              <div className="hidden md:block ml-2 min-w-0">
                <p
                  className={cn(
                    "text-xs font-medium truncate",
                    isCurrent ? "text-primary" : "text-muted-foreground"
                  )}
                >
                  {step.name}
                </p>
              </div>

              {/* Connector Line */}
              {index < WORKFLOW_STEPS.length - 1 && (
                <div
                  className={cn(
                    "flex-1 h-0.5 mx-2",
                    step.number < currentStep ? "bg-primary" : "bg-muted"
                  )}
                />
              )}
            </div>
          )
        })}
      </div>

      {/* Mobile: Show current step name */}
      <div className="md:hidden mt-2 text-center">
        <p className="text-sm font-medium text-primary">
          Step {currentStep}: {WORKFLOW_STEPS.find(s => s.number === currentStep)?.name}
        </p>
      </div>
    </div>
  )
}
