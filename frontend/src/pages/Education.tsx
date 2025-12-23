import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Link } from "react-router-dom"
import {
  BookOpen,
  Shield,
  Lightbulb,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Target,
  Layers,
  MessageSquare,
  FileText,
  Sparkles,
  Lock,
  ArrowRight,
  ExternalLink
} from "lucide-react"

// Best practice categories with detailed explanations
const bestPractices = [
  {
    id: "clarity",
    title: "Clarity & Specificity",
    points: 20,
    icon: Target,
    color: "text-blue-500",
    bgColor: "bg-blue-50 dark:bg-blue-950/20",
    description: "Be direct, unambiguous, and precise with your instructions.",
    source: "OpenAI GPT-5 Guidelines",
    doList: [
      "Use precise action verbs (analyze, list, compare, summarize)",
      "Define success criteria explicitly",
      "Specify exact requirements rather than vague goals",
      "Include word/length limits when relevant"
    ],
    dontList: [
      "Use vague words like 'good', 'appropriate', 'relevant', 'proper'",
      "Write contradictory or confusing instructions",
      "Leave requirements open to interpretation"
    ],
    example: {
      bad: "Write a summary of the article. Make it good and include the important parts.",
      good: "Summarize this article in exactly 3 bullet points, each under 25 words. Focus on the main argument, key evidence, and conclusion."
    }
  },
  {
    id: "structure",
    title: "Structure & Organization",
    points: 20,
    icon: Layers,
    color: "text-purple-500",
    bgColor: "bg-purple-50 dark:bg-purple-950/20",
    description: "Organize prompts with consistent delimiters and logical flow.",
    source: "Google DeepMind Research",
    doList: [
      "Use consistent XML tags (<context>, <task>, <format>)",
      "Or use consistent markdown headings (## Context, ## Task)",
      "Maintain logical section flow",
      "Place critical instructions at the beginning"
    ],
    dontList: [
      "Mix different delimiter styles (XML + markdown)",
      "Write wall-of-text prompts without structure",
      "Bury important instructions at the end"
    ],
    example: {
      bad: "You should help users and be helpful. Answer their questions about coding. Make sure to explain things clearly. You're a coding assistant.",
      good: "<role>\nYou are a senior software engineer specializing in Python and JavaScript.\n</role>\n\n<task>\nAnswer coding questions with clear explanations and working code examples.\n</task>\n\n<format>\nFor each question:\n1. Brief explanation (2-3 sentences)\n2. Code example with comments\n3. Common pitfalls to avoid\n</format>"
    }
  },
  {
    id: "role",
    title: "Role Definition",
    points: 15,
    icon: MessageSquare,
    color: "text-green-500",
    bgColor: "bg-green-50 dark:bg-green-950/20",
    description: "Define a specific persona with domain expertise and behavioral guidelines.",
    source: "Anthropic Guidelines",
    doList: [
      "Specify domain expertise (e.g., 'senior tax accountant')",
      "Include relevant experience level",
      "Define communication style or tone",
      "Add behavioral guidelines when needed"
    ],
    dontList: [
      "Use generic roles like 'helpful assistant'",
      "Skip role definition entirely",
      "Use contradictory persona traits"
    ],
    example: {
      bad: "You are a helpful assistant.",
      good: "You are a senior data scientist with 10 years of experience in machine learning and statistical analysis. You explain complex concepts in accessible terms while maintaining technical accuracy. You prefer practical examples over theoretical explanations."
    }
  },
  {
    id: "output",
    title: "Output Format Specification",
    points: 15,
    icon: FileText,
    color: "text-yellow-500",
    bgColor: "bg-yellow-50 dark:bg-yellow-950/20",
    description: "Explicitly specify the expected format, structure, and verbosity.",
    source: "OpenAI Best Practices",
    doList: [
      "Specify format explicitly (JSON, markdown, bullets, tables)",
      "Include length or verbosity constraints",
      "Provide structure templates when helpful",
      "Define response organization"
    ],
    dontList: [
      "Leave format completely open",
      "Use vague guidance like 'be concise' without limits",
      "Assume the model knows your preferred format"
    ],
    example: {
      bad: "Analyze this data and give me insights.",
      good: "Analyze this data and return a JSON object with:\n{\n  \"key_findings\": [3-5 bullet points],\n  \"trends\": [identify 2-3 patterns],\n  \"recommendations\": [2 actionable items],\n  \"confidence\": \"high/medium/low\"\n}"
    }
  },
  {
    id: "examples",
    title: "Few-Shot Examples",
    points: 15,
    icon: Lightbulb,
    color: "text-orange-500",
    bgColor: "bg-orange-50 dark:bg-orange-950/20",
    description: "Include 2-4 diverse examples showing input-output patterns.",
    source: "Google Research",
    doList: [
      "Include 2-4 diverse examples covering different scenarios",
      "Use consistent format: Input -> Output",
      "Show edge cases and varying complexity",
      "Demonstrate the quality level you expect"
    ],
    dontList: [
      "Skip examples for non-trivial tasks",
      "Use only simple/easy examples",
      "Use inconsistent example formats"
    ],
    example: {
      bad: "Classify the sentiment of customer reviews.",
      good: "Classify the sentiment of customer reviews as POSITIVE, NEGATIVE, or NEUTRAL.\n\nExamples:\nInput: \"This product is amazing! Best purchase ever.\"\nOutput: POSITIVE\n\nInput: \"It works, nothing special.\"\nOutput: NEUTRAL\n\nInput: \"Broke after one day. Terrible quality.\"\nOutput: NEGATIVE\n\nNow classify:\nInput: \"{{user_review}}\"\nOutput:"
    }
  },
  {
    id: "constraints",
    title: "Constraints & Boundaries",
    points: 10,
    icon: Shield,
    color: "text-red-500",
    bgColor: "bg-red-50 dark:bg-red-950/20",
    description: "Define clear boundaries, limitations, and escape hatches.",
    source: "OpenAI GPT-5 Guidelines",
    doList: [
      "Define what's in and out of scope",
      "Include 'do NOT' instructions for common failure modes",
      "Add escape hatches: 'If uncertain, state your assumptions'",
      "Handle edge cases explicitly"
    ],
    dontList: [
      "Leave prompts completely open-ended",
      "Assume the model knows implicit boundaries",
      "Skip negative instructions"
    ],
    example: {
      bad: "Help the user with their coding question.",
      good: "<constraints>\n- ONLY answer questions about Python and JavaScript\n- Do NOT write complete applications; focus on specific functions\n- If a question is ambiguous, ask for clarification\n- If you're unsure about best practices, state your assumptions\n- Maximum code snippet length: 50 lines\n</constraints>"
    }
  },
  {
    id: "reasoning",
    title: "Reasoning Guidance",
    points: 5,
    icon: Sparkles,
    color: "text-pink-500",
    bgColor: "bg-pink-50 dark:bg-pink-950/20",
    description: "Include chain-of-thought or step-by-step guidance for complex tasks.",
    source: "Anthropic Research",
    doList: [
      "Add 'Think through this step by step' for complex tasks",
      "Use <thinking> tags for internal reasoning",
      "Break down multi-step problems explicitly",
      "Request reasoning before final answers"
    ],
    dontList: [
      "Skip reasoning guidance for complex tasks",
      "Expect multi-step reasoning without instruction"
    ],
    example: {
      bad: "What is the answer to this math problem?",
      good: "Solve this math problem step by step:\n\n<thinking>\nFirst, identify what the problem is asking.\nThen, break it down into smaller steps.\nShow your work for each step.\nFinally, verify your answer.\n</thinking>\n\nProvide your final answer after showing your reasoning."
    }
  }
]

// Information to avoid sharing with AI
const privacyGuidelines = [
  {
    category: "Personal Identifiable Information (PII)",
    icon: Lock,
    items: [
      "Full names or real identities",
      "Social Security numbers or national IDs",
      "Home addresses or phone numbers",
      "Date of birth or age",
      "Email addresses (personal)",
      "Biometric data"
    ],
    severity: "critical"
  },
  {
    category: "Financial Information",
    icon: AlertTriangle,
    items: [
      "Credit card numbers or CVVs",
      "Bank account numbers",
      "Investment account details",
      "Tax information",
      "Salary or income details"
    ],
    severity: "critical"
  },
  {
    category: "Authentication Credentials",
    icon: Shield,
    items: [
      "Passwords or PINs",
      "API keys or secrets",
      "OAuth tokens",
      "Private encryption keys",
      "Two-factor authentication codes"
    ],
    severity: "critical"
  },
  {
    category: "Sensitive Business Information",
    icon: AlertTriangle,
    items: [
      "Trade secrets or proprietary algorithms",
      "Unreleased product information",
      "Internal financial projections",
      "Customer lists with identifiable data",
      "Confidential contracts"
    ],
    severity: "high"
  },
  {
    category: "Health Information",
    icon: Shield,
    items: [
      "Medical diagnoses or conditions",
      "Prescription information",
      "Mental health records",
      "Genetic information",
      "Health insurance details"
    ],
    severity: "critical"
  }
]

export function EducationPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link to="/" className="flex items-center gap-2">
              <BookOpen className="h-6 w-6 text-primary" />
              <span className="text-xl font-bold">Clarynt Education</span>
            </Link>
            <div className="flex items-center gap-4">
              <Link to="/docs">
                <Button variant="ghost">Documentation</Button>
              </Link>
              <Link to="/login">
                <Button>Get Started</Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-primary/5 to-background">
        <div className="max-w-4xl mx-auto text-center">
          <Badge className="mb-4" variant="secondary">
            <BookOpen className="h-3 w-3 mr-1" />
            Education Center
          </Badge>
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight mb-6">
            Best Practices for Prompting AI
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Learn research-backed techniques from OpenAI, Anthropic, and Google DeepMind
            to write prompts that get better results every time.
          </p>
        </div>
      </section>

      {/* Quick Stats */}
      <section className="py-12 px-4 sm:px-6 lg:px-8 border-b">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-3 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-primary mb-2">7</div>
              <div className="text-muted-foreground">Scoring Categories</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary mb-2">100</div>
              <div className="text-muted-foreground">Point Rubric</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary mb-2">3</div>
              <div className="text-muted-foreground">AI Lab Sources</div>
            </div>
          </div>
        </div>
      </section>

      {/* Scoring Overview */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">The 100-Point Scoring System</h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Clarynt evaluates prompts across 7 research-backed categories. Most prompts
              in the wild score under 40/100. Learn how to achieve 85+.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mb-12">
            {bestPractices.map((practice) => (
              <Card key={practice.id} className={`${practice.bgColor} border-0`}>
                <CardContent className="pt-6">
                  <practice.icon className={`h-8 w-8 ${practice.color} mb-3`} />
                  <div className="font-semibold">{practice.title}</div>
                  <div className="text-2xl font-bold mt-1">{practice.points} pts</div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Detailed Best Practices */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-muted/30">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold mb-12 text-center">Best Practices in Detail</h2>

          <div className="space-y-12">
            {bestPractices.map((practice) => (
              <Card key={practice.id} className="overflow-hidden">
                <CardHeader className={practice.bgColor}>
                  <div className="flex items-center gap-4">
                    <div className="h-12 w-12 rounded-full bg-white dark:bg-background flex items-center justify-center">
                      <practice.icon className={`h-6 w-6 ${practice.color}`} />
                    </div>
                    <div>
                      <div className="flex items-center gap-3">
                        <CardTitle className="text-xl">{practice.title}</CardTitle>
                        <Badge variant="outline">{practice.points} points</Badge>
                      </div>
                      <CardDescription className="text-foreground/70 mt-1">
                        Source: {practice.source}
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="pt-6 space-y-6">
                  <p className="text-lg">{practice.description}</p>

                  <div className="grid md:grid-cols-2 gap-6">
                    {/* Do List */}
                    <div>
                      <h4 className="font-semibold text-green-600 dark:text-green-400 mb-3 flex items-center gap-2">
                        <CheckCircle className="h-4 w-4" /> Do This
                      </h4>
                      <ul className="space-y-2">
                        {practice.doList.map((item, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm">
                            <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                            {item}
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Don't List */}
                    <div>
                      <h4 className="font-semibold text-red-600 dark:text-red-400 mb-3 flex items-center gap-2">
                        <XCircle className="h-4 w-4" /> Avoid This
                      </h4>
                      <ul className="space-y-2">
                        {practice.dontList.map((item, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm">
                            <XCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                            {item}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* Example */}
                  <div className="border-t pt-6">
                    <h4 className="font-semibold mb-4">Example Comparison</h4>
                    <div className="grid md:grid-cols-2 gap-4">
                      <div className="bg-red-50 dark:bg-red-950/20 p-4 rounded-lg border border-red-200 dark:border-red-800">
                        <div className="flex items-center gap-2 mb-2 text-red-600 dark:text-red-400 text-sm font-medium">
                          <XCircle className="h-4 w-4" /> Poor Example
                        </div>
                        <pre className="text-sm whitespace-pre-wrap font-mono">{practice.example.bad}</pre>
                      </div>
                      <div className="bg-green-50 dark:bg-green-950/20 p-4 rounded-lg border border-green-200 dark:border-green-800">
                        <div className="flex items-center gap-2 mb-2 text-green-600 dark:text-green-400 text-sm font-medium">
                          <CheckCircle className="h-4 w-4" /> Good Example
                        </div>
                        <pre className="text-sm whitespace-pre-wrap font-mono">{practice.example.good}</pre>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Privacy & Security Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <Badge variant="destructive" className="mb-4">
              <Shield className="h-3 w-3 mr-1" />
              Critical Security Information
            </Badge>
            <h2 className="text-3xl font-bold mb-4">Information to Never Include in Prompts</h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Protect yourself and others by never sharing sensitive information with AI systems.
              This data could be logged, stored, or used in ways you don't expect.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {privacyGuidelines.map((guideline) => (
              <Card
                key={guideline.category}
                className={`${
                  guideline.severity === "critical"
                    ? "border-red-200 dark:border-red-800"
                    : "border-yellow-200 dark:border-yellow-800"
                }`}
              >
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${
                      guideline.severity === "critical"
                        ? "bg-red-100 dark:bg-red-950/40"
                        : "bg-yellow-100 dark:bg-yellow-950/40"
                    }`}>
                      <guideline.icon className={`h-5 w-5 ${
                        guideline.severity === "critical"
                          ? "text-red-600"
                          : "text-yellow-600"
                      }`} />
                    </div>
                    <div>
                      <CardTitle className="text-base">{guideline.category}</CardTitle>
                      <Badge
                        variant={guideline.severity === "critical" ? "destructive" : "secondary"}
                        className="mt-1 text-xs"
                      >
                        {guideline.severity === "critical" ? "Never Share" : "Use Caution"}
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {guideline.items.map((item, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm">
                        <XCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                        {item}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>

          <Card className="mt-8 bg-primary/5 border-primary/20">
            <CardContent className="pt-6">
              <div className="flex items-start gap-4">
                <Shield className="h-8 w-8 text-primary flex-shrink-0" />
                <div>
                  <h3 className="font-semibold text-lg mb-2">Safe Prompting Guidelines</h3>
                  <ul className="space-y-2 text-muted-foreground">
                    <li className="flex items-start gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500 mt-1 flex-shrink-0" />
                      Use placeholder text or anonymized data when testing prompts
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500 mt-1 flex-shrink-0" />
                      Replace real names with generic terms (e.g., "User A", "Company X")
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500 mt-1 flex-shrink-0" />
                      Redact sensitive values in code snippets (use `[REDACTED]` or `***`)
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500 mt-1 flex-shrink-0" />
                      Review prompts before submitting to remove any accidental inclusions
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500 mt-1 flex-shrink-0" />
                      Use environment variables for API keys and secrets, never inline
                    </li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* CO-STAR Framework */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-muted/30">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">The CO-STAR Framework</h2>
            <p className="text-lg text-muted-foreground">
              A comprehensive structure for crafting effective prompts
            </p>
          </div>

          <div className="grid gap-4">
            {[
              { letter: "C", word: "Context", description: "Provide background information and relevant details" },
              { letter: "O", word: "Objective", description: "Clearly state what you want to accomplish" },
              { letter: "S", word: "Style", description: "Specify the writing style or format" },
              { letter: "T", word: "Tone", description: "Define the emotional tone (professional, casual, etc.)" },
              { letter: "A", word: "Audience", description: "Identify who will consume the output" },
              { letter: "R", word: "Response", description: "Describe the desired response format" }
            ].map((item) => (
              <div key={item.letter} className="flex items-center gap-4 p-4 bg-card rounded-lg border">
                <div className="h-12 w-12 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xl font-bold flex-shrink-0">
                  {item.letter}
                </div>
                <div>
                  <div className="font-semibold">{item.word}</div>
                  <div className="text-sm text-muted-foreground">{item.description}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-primary text-primary-foreground">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-6">Ready to Optimize Your Prompts?</h2>
          <p className="text-xl opacity-90 mb-8">
            Use Clarynt to automatically score and improve your prompts using these best practices.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/login">
              <Button size="lg" variant="secondary" className="text-lg px-8">
                Start Optimizing Free
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <Link to="/docs">
              <Button size="lg" variant="outline" className="text-lg px-8 bg-transparent border-primary-foreground/30 hover:bg-primary-foreground/10">
                Read Documentation
                <ExternalLink className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center text-sm text-muted-foreground">
          <p>&copy; {new Date().getFullYear()} Clarynt. All rights reserved.</p>
          <p className="mt-2">
            Best practices derived from official documentation and research from OpenAI, Anthropic, and Google DeepMind.
          </p>
        </div>
      </footer>
    </div>
  )
}
