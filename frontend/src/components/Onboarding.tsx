import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import {
  
  BarChart3,
  Sparkles,
  Code2,
  ArrowRight,
  ArrowLeft,
  Check,
  Copy,
  CheckCircle
} from "lucide-react"

interface OnboardingProps {
  apiKey: string
  onComplete: () => void
}

const steps = [
  {
    id: "welcome",
    title: "Welcome to PromptLab!",
    description: "Let's get you set up to optimize your LLM operations.",
  },
  {
    id: "features",
    title: "What you can do",
    description: "PromptLab helps you build better AI products.",
  },
  {
    id: "integrate",
    title: "Integrate the SDK",
    description: "Start logging requests in minutes.",
  },
  {
    id: "optimize",
    title: "Try the Optimizer",
    description: "Improve your prompts with AI assistance.",
  },
]

export function Onboarding({ apiKey, onComplete }: OnboardingProps) {
  const navigate = useNavigate()
  const [currentStep, setCurrentStep] = useState(0)
  const [copied, setCopied] = useState(false)

  const step = steps[currentStep]
  const isLastStep = currentStep === steps.length - 1

  const copyCode = (code: string) => {
    navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleNext = () => {
    if (isLastStep) {
      onComplete()
    } else {
      setCurrentStep((s) => s + 1)
    }
  }

  const handleBack = () => {
    setCurrentStep((s) => s - 1)
  }

  const handleSkip = () => {
    onComplete()
  }

  const handleGoToOptimizer = () => {
    onComplete()
    navigate("/agents")
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/30 p-4">
      <Card className="w-full max-w-2xl">
        {/* Progress indicator */}
        <div className="p-4 border-b">
          <div className="flex items-center justify-between">
            {steps.map((s, i) => (
              <div key={s.id} className="flex items-center">
                <div
                  className={`h-8 w-8 rounded-full flex items-center justify-center text-sm font-medium ${
                    i < currentStep
                      ? "bg-primary text-primary-foreground"
                      : i === currentStep
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted text-muted-foreground"
                  }`}
                >
                  {i < currentStep ? <Check className="h-4 w-4" /> : i + 1}
                </div>
                {i < steps.length - 1 && (
                  <div
                    className={`h-1 w-12 sm:w-20 mx-2 ${
                      i < currentStep ? "bg-primary" : "bg-muted"
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        <CardHeader className="text-center">
          <CardTitle className="text-2xl">{step.title}</CardTitle>
          <CardDescription className="text-base">{step.description}</CardDescription>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Welcome Step */}
          {step.id === "welcome" && (
            <div className="text-center space-y-4">
              <div className="mx-auto h-20 w-20 rounded-full bg-primary/10 flex items-center justify-center">
                <img src="/clarynt_icon.jpg" alt="Clarynt" className="h-10 w-10" />
              </div>
              <p className="text-muted-foreground">
                PromptLab is your complete platform for logging, monitoring, and optimizing LLM API calls.
                In the next few steps, we'll show you how to get the most out of it.
              </p>
              <div className="p-4 bg-muted rounded-lg">
                <div className="text-sm font-medium mb-2">Your API Key</div>
                <div className="flex items-center gap-2">
                  <code className="flex-1 p-2 bg-background rounded border text-sm font-mono overflow-hidden text-ellipsis">
                    {apiKey.slice(0, 20)}...
                  </code>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => copyCode(apiKey)}
                  >
                    {copied ? <CheckCircle className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                  </Button>
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  Keep this safe - you'll need it to integrate the SDK.
                </p>
              </div>
            </div>
          )}

          {/* Features Step */}
          {step.id === "features" && (
            <div className="grid gap-4">
              <div className="flex items-start gap-4 p-4 rounded-lg bg-muted/50">
                <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                  <BarChart3 className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <h4 className="font-medium">Request Logging</h4>
                  <p className="text-sm text-muted-foreground">
                    Automatically capture every LLM API call with full request/response data,
                    token counts, latency metrics, and costs.
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-4 p-4 rounded-lg bg-muted/50">
                <div className="h-10 w-10 rounded-lg bg-purple-100 flex items-center justify-center flex-shrink-0">
                  <Sparkles className="h-5 w-5 text-purple-600" />
                </div>
                <div>
                  <h4 className="font-medium">Prompt Optimization</h4>
                  <p className="text-sm text-muted-foreground">
                    Use AI to analyze your prompts and get specific, actionable improvements
                    based on proven prompt engineering techniques.
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-4 p-4 rounded-lg bg-muted/50">
                <div className="h-10 w-10 rounded-lg bg-green-100 flex items-center justify-center flex-shrink-0">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                </div>
                <div>
                  <h4 className="font-medium">Quality Scoring</h4>
                  <p className="text-sm text-muted-foreground">
                    Every response is automatically evaluated for quality, helping you
                    identify issues and track improvements over time.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Integrate Step */}
          {step.id === "integrate" && (
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Code2 className="h-4 w-4" />
                <span>Python SDK Integration</span>
              </div>

              <div className="space-y-3">
                <div>
                  <div className="text-sm font-medium mb-2">1. Install the SDK</div>
                  <div className="relative">
                    <pre className="p-3 bg-muted rounded-lg text-sm font-mono overflow-x-auto">
                      pip install promptlab
                    </pre>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="absolute top-2 right-2"
                      onClick={() => copyCode("pip install promptlab")}
                    >
                      <Copy className="h-4 w-4" />
                    </Button>
                  </div>
                </div>

                <div>
                  <div className="text-sm font-medium mb-2">2. Track your OpenAI calls</div>
                  <div className="relative">
                    <pre className="p-3 bg-muted rounded-lg text-sm font-mono overflow-x-auto whitespace-pre-wrap">
{`from promptlab import track
from openai import OpenAI

client = track(OpenAI(), api_key="${apiKey.slice(0, 16)}...")

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)`}
                    </pre>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="absolute top-2 right-2"
                      onClick={() => copyCode(`from promptlab import track
from openai import OpenAI

client = track(OpenAI(), api_key="${apiKey}")

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)`)}
                    >
                      <Copy className="h-4 w-4" />
                    </Button>
                  </div>
                </div>

                <p className="text-sm text-muted-foreground">
                  That's it! All your OpenAI calls will now be logged to PromptLab
                  and appear in your dashboard.
                </p>
              </div>
            </div>
          )}

          {/* Optimize Step */}
          {step.id === "optimize" && (
            <div className="text-center space-y-6">
              <div className="mx-auto h-20 w-20 rounded-full bg-purple-100 flex items-center justify-center">
                <Sparkles className="h-10 w-10 text-purple-600" />
              </div>
              <div className="space-y-2">
                <p className="text-muted-foreground">
                  You're all set! Try our AI-powered Prompt Optimizer to improve your prompts instantly.
                </p>
                <p className="text-sm text-muted-foreground">
                  Just paste your prompt, describe what it should do, and get specific improvement suggestions.
                </p>
              </div>
              <Button size="lg" onClick={handleGoToOptimizer}>
                <Sparkles className="h-4 w-4 mr-2" />
                Try the Optimizer
              </Button>
            </div>
          )}
        </CardContent>

        {/* Navigation */}
        <div className="p-6 border-t flex items-center justify-between">
          <div>
            {currentStep > 0 && (
              <Button variant="ghost" onClick={handleBack}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
            )}
          </div>
          <div className="flex items-center gap-2">
            {!isLastStep && (
              <Button variant="ghost" onClick={handleSkip}>
                Skip tour
              </Button>
            )}
            <Button onClick={handleNext}>
              {isLastStep ? (
                "Go to Dashboard"
              ) : (
                <>
                  Next
                  <ArrowRight className="h-4 w-4 ml-2" />
                </>
              )}
            </Button>
          </div>
        </div>
      </Card>
    </div>
  )
}
