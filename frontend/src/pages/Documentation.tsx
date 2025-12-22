import { useState } from "react"
import { Link } from "react-router-dom"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  BookOpen,
  Zap,
  LayoutDashboard,
  Sparkles,
  Gavel,
  Scale,
  Library,
  Settings,
  Key,
  Code2,
  ArrowRight,
  Copy,
  Check,
  ExternalLink,
  Play,
  AlertCircle,
  Info
} from "lucide-react"

// Documentation sections
const sections = [
  { id: "getting-started", title: "Getting Started", icon: Play },
  { id: "dashboard", title: "Dashboard", icon: LayoutDashboard },
  { id: "prompt-optimizer", title: "Prompt Optimizer", icon: Sparkles },
  { id: "judge-evaluator", title: "Judge Evaluator", icon: Gavel },
  { id: "response-compare", title: "Response Comparison", icon: Scale },
  { id: "prompt-library", title: "Prompt Library", icon: Library },
  { id: "settings", title: "Settings & API Keys", icon: Settings },
  { id: "sdk", title: "Python SDK", icon: Code2 },
  { id: "pricing", title: "Pricing & Limits", icon: Zap }
]

export function DocumentationPage() {
  const [activeSection, setActiveSection] = useState("getting-started")
  const [copiedCode, setCopiedCode] = useState<string | null>(null)

  const copyCode = (code: string, id: string) => {
    navigator.clipboard.writeText(code)
    setCopiedCode(id)
    setTimeout(() => setCopiedCode(null), 2000)
  }

  const CodeBlock = ({ code, id }: { code: string; id: string }) => (
    <div className="relative">
      <pre className="bg-muted p-4 rounded-lg text-sm overflow-x-auto font-mono">
        <code>{code}</code>
      </pre>
      <Button
        variant="ghost"
        size="sm"
        className="absolute top-2 right-2"
        onClick={() => copyCode(code, id)}
      >
        {copiedCode === id ? (
          <Check className="h-4 w-4 text-green-500" />
        ) : (
          <Copy className="h-4 w-4" />
        )}
      </Button>
    </div>
  )

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link to="/" className="flex items-center gap-2">
              <BookOpen className="h-6 w-6 text-primary" />
              <span className="text-xl font-bold">PromptLab Docs</span>
            </Link>
            <div className="flex items-center gap-4">
              <Link to="/education">
                <Button variant="ghost">Best Practices</Button>
              </Link>
              <Link to="/login">
                <Button>Get Started</Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-8">
          {/* Sidebar */}
          <aside className="w-64 flex-shrink-0 hidden lg:block">
            <div className="sticky top-24 space-y-1">
              <h3 className="font-semibold mb-4 text-muted-foreground text-sm uppercase tracking-wider">
                Documentation
              </h3>
              {sections.map((section) => (
                <button
                  key={section.id}
                  onClick={() => setActiveSection(section.id)}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left text-sm transition-colors ${
                    activeSection === section.id
                      ? "bg-primary/10 text-primary font-medium"
                      : "text-muted-foreground hover:text-foreground hover:bg-muted"
                  }`}
                >
                  <section.icon className="h-4 w-4" />
                  {section.title}
                </button>
              ))}
            </div>
          </aside>

          {/* Main Content */}
          <main className="flex-1 min-w-0">
            {/* Mobile Section Selector */}
            <div className="lg:hidden mb-6">
              <select
                value={activeSection}
                onChange={(e) => setActiveSection(e.target.value)}
                className="w-full p-3 border rounded-lg bg-background"
              >
                {sections.map((section) => (
                  <option key={section.id} value={section.id}>
                    {section.title}
                  </option>
                ))}
              </select>
            </div>

            {/* Getting Started */}
            {activeSection === "getting-started" && (
              <div className="space-y-8">
                <div>
                  <Badge variant="secondary" className="mb-4">Getting Started</Badge>
                  <h1 className="text-4xl font-bold mb-4">Welcome to PromptLab</h1>
                  <p className="text-lg text-muted-foreground">
                    PromptLab is an LLMOps platform for prompt optimization, testing, and monitoring.
                    Get better results from AI by writing research-backed prompts.
                  </p>
                </div>

                <Card>
                  <CardHeader>
                    <CardTitle>Quick Start Guide</CardTitle>
                    <CardDescription>Get up and running in under 5 minutes</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="flex items-start gap-4">
                      <div className="h-8 w-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-bold flex-shrink-0">1</div>
                      <div>
                        <h3 className="font-semibold mb-2">Create an Account</h3>
                        <p className="text-muted-foreground mb-2">
                          Sign up for free at PromptLab. No credit card required.
                        </p>
                        <Link to="/login">
                          <Button variant="outline" size="sm">
                            Sign Up <ArrowRight className="h-4 w-4 ml-2" />
                          </Button>
                        </Link>
                      </div>
                    </div>

                    <div className="flex items-start gap-4">
                      <div className="h-8 w-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-bold flex-shrink-0">2</div>
                      <div>
                        <h3 className="font-semibold mb-2">Optimize Your First Prompt</h3>
                        <p className="text-muted-foreground">
                          Navigate to the <strong>Agent Tools</strong> page, paste your prompt, describe what it should do,
                          and click "Optimize Prompt". Watch your score improve.
                        </p>
                      </div>
                    </div>

                    <div className="flex items-start gap-4">
                      <div className="h-8 w-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-bold flex-shrink-0">3</div>
                      <div>
                        <h3 className="font-semibold mb-2">Set Up Request Logging (Optional)</h3>
                        <p className="text-muted-foreground mb-2">
                          Install the Python SDK to automatically log all your LLM API calls.
                        </p>
                        <CodeBlock
                          id="install-sdk"
                          code={`pip install promptlab-sdk`}
                        />
                      </div>
                    </div>

                    <div className="flex items-start gap-4">
                      <div className="h-8 w-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-bold flex-shrink-0">4</div>
                      <div>
                        <h3 className="font-semibold mb-2">Monitor and Improve</h3>
                        <p className="text-muted-foreground">
                          View logged requests in the Dashboard, evaluate responses with the Judge,
                          and save optimized prompts to your Library.
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-primary/5 border-primary/20">
                  <CardContent className="pt-6">
                    <div className="flex items-start gap-4">
                      <Info className="h-6 w-6 text-primary flex-shrink-0" />
                      <div>
                        <h3 className="font-semibold mb-2">Free Tier Includes</h3>
                        <ul className="text-muted-foreground space-y-1">
                          <li>1,000 logged requests per month</li>
                          <li>10 prompt optimizations per month</li>
                          <li>7-day data retention</li>
                          <li>Basic analytics</li>
                        </ul>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Dashboard */}
            {activeSection === "dashboard" && (
              <div className="space-y-8">
                <div>
                  <Badge variant="secondary" className="mb-4">
                    <LayoutDashboard className="h-3 w-3 mr-1" />
                    Dashboard
                  </Badge>
                  <h1 className="text-4xl font-bold mb-4">Request Dashboard</h1>
                  <p className="text-lg text-muted-foreground">
                    View and analyze all logged LLM API requests in real-time.
                  </p>
                </div>

                <Card>
                  <CardHeader>
                    <CardTitle>Dashboard Overview</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div>
                      <h3 className="font-semibold mb-2">Statistics Cards</h3>
                      <p className="text-muted-foreground mb-4">
                        The top of the dashboard displays key metrics:
                      </p>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="p-4 bg-muted rounded-lg">
                          <div className="text-sm text-muted-foreground">Total Requests</div>
                          <div className="text-2xl font-bold">Number of logged API calls</div>
                        </div>
                        <div className="p-4 bg-muted rounded-lg">
                          <div className="text-sm text-muted-foreground">Avg Quality Score</div>
                          <div className="text-2xl font-bold">Mean score of evaluated responses</div>
                        </div>
                        <div className="p-4 bg-muted rounded-lg">
                          <div className="text-sm text-muted-foreground">Total Tokens</div>
                          <div className="text-2xl font-bold">Combined input + output tokens</div>
                        </div>
                        <div className="p-4 bg-muted rounded-lg">
                          <div className="text-sm text-muted-foreground">Avg Latency</div>
                          <div className="text-2xl font-bold">Mean response time in ms</div>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h3 className="font-semibold mb-2">Request List</h3>
                      <p className="text-muted-foreground">
                        View all logged requests sorted by recency. Each request shows:
                      </p>
                      <ul className="list-disc list-inside mt-2 text-muted-foreground space-y-1">
                        <li>Model used (e.g., GPT-4, Claude, etc.)</li>
                        <li>Quality score (if evaluated)</li>
                        <li>Timestamp</li>
                        <li>Latency and token count</li>
                        <li>Evaluation tags</li>
                      </ul>
                    </div>

                    <div>
                      <h3 className="font-semibold mb-2">Request Details</h3>
                      <p className="text-muted-foreground">
                        Click any request to view full details including:
                      </p>
                      <ul className="list-disc list-inside mt-2 text-muted-foreground space-y-1">
                        <li>Full message history (system, user, assistant messages)</li>
                        <li>Complete response content</li>
                        <li>Detailed evaluation breakdown with scores and rationale</li>
                        <li>Trace ID and metadata</li>
                      </ul>
                    </div>

                    <div className="p-4 bg-muted rounded-lg">
                      <h4 className="font-semibold mb-2 flex items-center gap-2">
                        <Gavel className="h-4 w-4" /> Quick Evaluation
                      </h4>
                      <p className="text-sm text-muted-foreground">
                        Click the "Evaluate" button on any request to send it to the Judge agent
                        for scoring. Evaluated requests show quality scores and feedback tags.
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Prompt Optimizer */}
            {activeSection === "prompt-optimizer" && (
              <div className="space-y-8">
                <div>
                  <Badge variant="secondary" className="mb-4">
                    <Sparkles className="h-3 w-3 mr-1" />
                    Agent Tools
                  </Badge>
                  <h1 className="text-4xl font-bold mb-4">Prompt Optimizer</h1>
                  <p className="text-lg text-muted-foreground">
                    Transform vague prompts into precise, high-scoring instructions using
                    AI-powered optimization based on 2025 best practices.
                  </p>
                </div>

                <Card>
                  <CardHeader>
                    <CardTitle>How It Works</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="grid gap-6">
                      <div>
                        <h3 className="font-semibold mb-2">Step 1: Enter Your Prompt</h3>
                        <p className="text-muted-foreground">
                          Paste the prompt you want to improve in the "Your Current Prompt" field.
                          This can be any prompt template you're using with an LLM.
                        </p>
                      </div>

                      <div>
                        <h3 className="font-semibold mb-2">Step 2: Describe the Task</h3>
                        <p className="text-muted-foreground">
                          Tell us what your prompt should accomplish. For example:
                          "Summarize articles", "Write marketing copy", or "Answer customer questions".
                        </p>
                      </div>

                      <div>
                        <h3 className="font-semibold mb-2">Step 3: Add Example Inputs (Optional)</h3>
                        <p className="text-muted-foreground">
                          Provide example user inputs, one per line. This helps the optimizer
                          generate better few-shot examples for your specific use case.
                        </p>
                      </div>

                      <div>
                        <h3 className="font-semibold mb-2">Step 4: Review Results</h3>
                        <p className="text-muted-foreground">
                          After optimization, you'll see:
                        </p>
                        <ul className="list-disc list-inside mt-2 text-muted-foreground space-y-1">
                          <li><strong>Score Comparison:</strong> Original vs. optimized score (0-10 scale)</li>
                          <li><strong>Improvements Made:</strong> List of specific changes</li>
                          <li><strong>Side-by-Side View:</strong> Original and optimized prompts</li>
                          <li><strong>Analysis Details:</strong> Issues found and strengths</li>
                          <li><strong>Few-Shot Examples:</strong> Auto-generated examples</li>
                        </ul>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-primary/50">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      Optimization Modes
                      <Badge>New</Badge>
                    </CardTitle>
                    <CardDescription>Choose the right mode for your needs</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="grid md:grid-cols-2 gap-6">
                      <div className="p-4 bg-muted rounded-lg">
                        <h4 className="font-semibold mb-2">Standard Mode</h4>
                        <Badge variant="secondary" className="mb-3">Free Tier</Badge>
                        <ul className="text-sm text-muted-foreground space-y-2">
                          <li>5 LLM calls per optimization</li>
                          <li>AI-generated few-shot examples</li>
                          <li>Basic prompt analysis</li>
                          <li>~1.5 cents per optimization</li>
                        </ul>
                      </div>
                      <div className="p-4 bg-primary/5 border border-primary/20 rounded-lg">
                        <h4 className="font-semibold mb-2">Enhanced Mode</h4>
                        <Badge className="mb-3">Pro / Team / Enterprise</Badge>
                        <ul className="text-sm text-muted-foreground space-y-2">
                          <li>7-8 LLM calls + web search</li>
                          <li>Real few-shot examples from web research</li>
                          <li>Judge evaluation before returning</li>
                          <li>Automatic retry if regression detected</li>
                          <li>~3-4 cents per optimization</li>
                        </ul>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-semibold mb-2">Enhanced Mode Features</h4>
                      <div className="space-y-3">
                        <div className="flex items-start gap-3">
                          <div className="h-6 w-6 rounded-full bg-blue-500/20 text-blue-500 flex items-center justify-center flex-shrink-0 text-sm font-bold">1</div>
                          <div>
                            <p className="font-medium">Web-Enhanced Few-Shot Examples</p>
                            <p className="text-sm text-muted-foreground">
                              Instead of AI-fabricated examples, enhanced mode searches real documentation,
                              GitHub repositories, and best practices to create grounded few-shot examples.
                              Sources are included in the response.
                            </p>
                          </div>
                        </div>
                        <div className="flex items-start gap-3">
                          <div className="h-6 w-6 rounded-full bg-purple-500/20 text-purple-500 flex items-center justify-center flex-shrink-0 text-sm font-bold">2</div>
                          <div>
                            <p className="font-medium">Judge Evaluation</p>
                            <p className="text-sm text-muted-foreground">
                              Before returning, the Judge agent evaluates the optimized prompt against
                              the original to detect any regressions. You'll see a quality score,
                              improvement margin, and detailed rationale.
                            </p>
                          </div>
                        </div>
                        <div className="flex items-start gap-3">
                          <div className="h-6 w-6 rounded-full bg-green-500/20 text-green-500 flex items-center justify-center flex-shrink-0 text-sm font-bold">3</div>
                          <div>
                            <p className="font-medium">Automatic Retry</p>
                            <p className="text-sm text-muted-foreground">
                              If the Judge detects a regression (optimization made it worse),
                              the system automatically retries with feedback to produce a better result.
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Scoring Categories</CardTitle>
                    <CardDescription>Prompts are scored across 7 research-backed categories</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {[
                        { name: "Clarity & Specificity", points: 20, color: "bg-blue-500" },
                        { name: "Structure & Organization", points: 20, color: "bg-purple-500" },
                        { name: "Role Definition", points: 15, color: "bg-green-500" },
                        { name: "Output Format", points: 15, color: "bg-yellow-500" },
                        { name: "Few-Shot Examples", points: 15, color: "bg-orange-500" },
                        { name: "Constraints & Boundaries", points: 10, color: "bg-red-500" },
                        { name: "Reasoning Guidance", points: 5, color: "bg-pink-500" }
                      ].map((category) => (
                        <div key={category.name} className="flex items-center gap-4">
                          <div className={`h-3 w-3 rounded-full ${category.color}`} />
                          <span className="flex-1">{category.name}</span>
                          <span className="font-mono font-semibold">{category.points} pts</span>
                        </div>
                      ))}
                    </div>
                    <div className="mt-6 text-center">
                      <Link to="/education">
                        <Button variant="outline">
                          Learn Best Practices <ExternalLink className="h-4 w-4 ml-2" />
                        </Button>
                      </Link>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Judge Evaluator */}
            {activeSection === "judge-evaluator" && (
              <div className="space-y-8">
                <div>
                  <Badge variant="secondary" className="mb-4">
                    <Gavel className="h-3 w-3 mr-1" />
                    Agent Tools
                  </Badge>
                  <h1 className="text-4xl font-bold mb-4">Judge Evaluator</h1>
                  <p className="text-lg text-muted-foreground">
                    Evaluate AI responses for quality, correctness, and potential hallucinations.
                  </p>
                </div>

                <Card>
                  <CardHeader>
                    <CardTitle>Evaluation Process</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div>
                      <h3 className="font-semibold mb-2">Input Fields</h3>
                      <ul className="list-disc list-inside text-muted-foreground space-y-2">
                        <li><strong>Request / Prompt:</strong> The original user request or prompt</li>
                        <li><strong>Response to Evaluate:</strong> The AI-generated response</li>
                        <li><strong>Custom Rubric (Optional):</strong> Define your own evaluation criteria</li>
                      </ul>
                    </div>

                    <div>
                      <h3 className="font-semibold mb-2">Evaluation Results</h3>
                      <p className="text-muted-foreground mb-3">
                        The Judge provides a comprehensive evaluation including:
                      </p>
                      <div className="grid md:grid-cols-2 gap-4">
                        <div className="p-4 bg-muted rounded-lg">
                          <h4 className="font-medium mb-2">Scores (0-5 scale)</h4>
                          <ul className="text-sm text-muted-foreground space-y-1">
                            <li>Correctness (0-4)</li>
                            <li>Completeness (0-3)</li>
                            <li>Clarity (0-2)</li>
                            <li>Safety (0-1)</li>
                          </ul>
                        </div>
                        <div className="p-4 bg-muted rounded-lg">
                          <h4 className="font-medium mb-2">Qualitative Feedback</h4>
                          <ul className="text-sm text-muted-foreground space-y-1">
                            <li>Strengths identified</li>
                            <li>Weaknesses identified</li>
                            <li>Detailed reasoning</li>
                          </ul>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h3 className="font-semibold mb-2">Hallucination Detection</h3>
                      <p className="text-muted-foreground">
                        The Judge also performs fact-checking and identifies:
                      </p>
                      <ul className="list-disc list-inside mt-2 text-muted-foreground space-y-1">
                        <li><strong className="text-red-500">Contradicted Claims:</strong> Statements that conflict with known facts</li>
                        <li><strong className="text-green-500">Verified Claims:</strong> Statements confirmed as accurate</li>
                        <li><strong className="text-yellow-500">Unverified Claims:</strong> Statements that couldn't be confirmed</li>
                      </ul>
                    </div>

                    <div>
                      <h3 className="font-semibold mb-2">Automatic Tags</h3>
                      <div className="flex flex-wrap gap-2">
                        <Badge>good</Badge>
                        <Badge variant="destructive">hallucination</Badge>
                        <Badge variant="secondary">missing_key_detail</Badge>
                        <Badge variant="destructive">unsafe</Badge>
                        <Badge variant="secondary">needs_improvement</Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Response Comparison */}
            {activeSection === "response-compare" && (
              <div className="space-y-8">
                <div>
                  <Badge variant="secondary" className="mb-4">
                    <Scale className="h-3 w-3 mr-1" />
                    Agent Tools
                  </Badge>
                  <h1 className="text-4xl font-bold mb-4">Response Comparison</h1>
                  <p className="text-lg text-muted-foreground">
                    Compare two AI responses side-by-side to determine which performs better.
                  </p>
                </div>

                <Card>
                  <CardHeader>
                    <CardTitle>How to Compare</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div>
                      <h3 className="font-semibold mb-2">Input Fields</h3>
                      <ul className="list-disc list-inside text-muted-foreground space-y-2">
                        <li><strong>Request / Prompt:</strong> The original query both responses address</li>
                        <li><strong>Response A:</strong> The first response to compare (optionally select the model)</li>
                        <li><strong>Response B:</strong> The second response to compare (optionally select the model)</li>
                        <li><strong>Custom Rubric:</strong> Optional criteria for comparison</li>
                      </ul>
                    </div>

                    <div>
                      <h3 className="font-semibold mb-2">Comparison Results</h3>
                      <p className="text-muted-foreground mb-3">
                        The comparison provides:
                      </p>
                      <ul className="list-disc list-inside text-muted-foreground space-y-2">
                        <li><strong>Winner:</strong> Which response is better (A, B, or Tie)</li>
                        <li><strong>Confidence:</strong> How confident the Judge is in the decision</li>
                        <li><strong>Criterion Breakdown:</strong> Which response wins on each evaluation dimension</li>
                        <li><strong>Reasoning:</strong> Explanation of why one response is preferred</li>
                        <li><strong>Hallucination Check:</strong> Fact verification for both responses</li>
                      </ul>
                    </div>

                    <div className="p-4 bg-muted rounded-lg">
                      <h4 className="font-semibold mb-2 flex items-center gap-2">
                        <Info className="h-4 w-4" /> Use Cases
                      </h4>
                      <ul className="text-sm text-muted-foreground space-y-1">
                        <li>Compare responses from different LLM providers</li>
                        <li>A/B test prompt variations</li>
                        <li>Evaluate model upgrades</li>
                        <li>Benchmark fine-tuned models against base models</li>
                      </ul>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Prompt Library */}
            {activeSection === "prompt-library" && (
              <div className="space-y-8">
                <div>
                  <Badge variant="secondary" className="mb-4">
                    <Library className="h-3 w-3 mr-1" />
                    Prompt Library
                  </Badge>
                  <h1 className="text-4xl font-bold mb-4">Prompt Library</h1>
                  <p className="text-lg text-muted-foreground">
                    Save and manage your optimized prompts for easy reuse.
                  </p>
                </div>

                <Card>
                  <CardHeader>
                    <CardTitle>Features</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div>
                      <h3 className="font-semibold mb-2">Saved Optimizations</h3>
                      <p className="text-muted-foreground">
                        When you optimize a prompt and click "Save to Library", it's stored with:
                      </p>
                      <ul className="list-disc list-inside mt-2 text-muted-foreground space-y-1">
                        <li>Task description</li>
                        <li>Original prompt</li>
                        <li>Optimized prompt</li>
                        <li>Before/after scores</li>
                      </ul>
                    </div>

                    <div>
                      <h3 className="font-semibold mb-2">Library View</h3>
                      <p className="text-muted-foreground">
                        The library displays all saved prompts as expandable cards:
                      </p>
                      <ul className="list-disc list-inside mt-2 text-muted-foreground space-y-1">
                        <li>Click any card to expand and view both versions</li>
                        <li>Copy either version to clipboard with one click</li>
                        <li>Search through your saved prompts</li>
                      </ul>
                    </div>

                    <div className="p-4 bg-muted rounded-lg">
                      <h4 className="font-semibold mb-2 flex items-center gap-2">
                        <AlertCircle className="h-4 w-4" /> Retention Policy
                      </h4>
                      <p className="text-sm text-muted-foreground">
                        Saved prompts are retained based on your subscription tier:
                        Free (7 days), Premium (30 days), Pro (90 days), Enterprise (unlimited).
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Settings & API Keys */}
            {activeSection === "settings" && (
              <div className="space-y-8">
                <div>
                  <Badge variant="secondary" className="mb-4">
                    <Settings className="h-3 w-3 mr-1" />
                    Settings
                  </Badge>
                  <h1 className="text-4xl font-bold mb-4">Settings & API Keys</h1>
                  <p className="text-lg text-muted-foreground">
                    Manage your organization, subscription, and API access.
                  </p>
                </div>

                <Card>
                  <CardHeader>
                    <CardTitle>Subscription & Billing</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div>
                      <h3 className="font-semibold mb-2">Current Plan</h3>
                      <p className="text-muted-foreground">
                        View your current subscription tier, status, and renewal date.
                        Premium and Pro users can manage their billing through Stripe.
                      </p>
                    </div>

                    <div>
                      <h3 className="font-semibold mb-2">Usage Tracking</h3>
                      <p className="text-muted-foreground">
                        Monitor your monthly usage against your plan limits:
                      </p>
                      <ul className="list-disc list-inside mt-2 text-muted-foreground space-y-1">
                        <li>API Requests used / limit</li>
                        <li>Prompt Optimizations used / limit</li>
                        <li>Token usage and estimated cost (for LLM calls)</li>
                      </ul>
                    </div>

                    <div>
                      <h3 className="font-semibold mb-2">Upgrade Options</h3>
                      <p className="text-muted-foreground">
                        Free users can upgrade directly from the Settings page.
                        Payment is processed securely through Stripe.
                      </p>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Key className="h-5 w-5" />
                      API Key Management
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div>
                      <h3 className="font-semibold mb-2">Creating API Keys</h3>
                      <p className="text-muted-foreground mb-4">
                        API keys are used to authenticate SDK requests and direct API calls.
                      </p>
                      <ol className="list-decimal list-inside text-muted-foreground space-y-2">
                        <li>Enter an optional name for the key</li>
                        <li>Click "Create Key"</li>
                        <li><strong>Copy the key immediately</strong> - it won't be shown again</li>
                        <li>Store securely (environment variable recommended)</li>
                      </ol>
                    </div>

                    <div className="p-4 bg-yellow-50 dark:bg-yellow-950/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                      <h4 className="font-semibold mb-2 flex items-center gap-2 text-yellow-800 dark:text-yellow-200">
                        <AlertCircle className="h-4 w-4" /> Security Warning
                      </h4>
                      <p className="text-sm text-yellow-700 dark:text-yellow-300">
                        API keys grant full access to your organization's PromptLab resources.
                        Never commit them to version control or share them publicly.
                      </p>
                    </div>

                    <div>
                      <h3 className="font-semibold mb-2">Managing Keys</h3>
                      <ul className="list-disc list-inside text-muted-foreground space-y-1">
                        <li>View all active keys (prefix shown for identification)</li>
                        <li>See creation date for each key</li>
                        <li>Delete keys that are no longer needed</li>
                      </ul>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Python SDK */}
            {activeSection === "sdk" && (
              <div className="space-y-8">
                <div>
                  <Badge variant="secondary" className="mb-4">
                    <Code2 className="h-3 w-3 mr-1" />
                    SDK
                  </Badge>
                  <h1 className="text-4xl font-bold mb-4">Python SDK</h1>
                  <p className="text-lg text-muted-foreground">
                    Integrate PromptLab into your Python applications for automatic request logging.
                  </p>
                </div>

                <Card>
                  <CardHeader>
                    <CardTitle>Installation</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CodeBlock
                      id="sdk-install"
                      code="pip install promptlab-sdk"
                    />
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Quick Start: Wrap OpenAI Client</CardTitle>
                    <CardDescription>The simplest way to start logging requests</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <CodeBlock
                      id="sdk-wrap"
                      code={`from promptlab import track
from openai import OpenAI

# Wrap your OpenAI client - all calls are automatically logged
client = track(OpenAI(), api_key="your_promptlab_api_key")

# Use normally - requests are logged in the background
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.choices[0].message.content)`}
                    />
                    <p className="text-sm text-muted-foreground mt-4">
                      The SDK wraps your OpenAI client and logs all requests in the background
                      without blocking your application.
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Manual Logging</CardTitle>
                    <CardDescription>For custom providers or more control</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <CodeBlock
                      id="sdk-manual"
                      code={`from promptlab import PromptLab

lab = PromptLab(api_key="your_promptlab_api_key")

# Log a request manually
lab.api.log_request({
    "model": "claude-3-opus",
    "provider": "anthropic",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is Python?"}
    ],
    "response_content": "Python is a high-level programming language...",
    "latency_ms": 1250,
    "input_tokens": 25,
    "output_tokens": 150,
    "trace_id": "optional-trace-id",
    "tags": ["production", "user-query"]
})`}
                    />
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Environment Variables</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-muted-foreground mb-4">
                      Configure the SDK using environment variables:
                    </p>
                    <CodeBlock
                      id="sdk-env"
                      code={`# Required
export PROMPTLAB_API_KEY="your_api_key"

# Optional - defaults to PromptLab cloud
export PROMPTLAB_BASE_URL="https://api.promptlab.dev"`}
                    />
                    <p className="text-sm text-muted-foreground mt-4">
                      When environment variables are set, you can initialize without parameters:
                    </p>
                    <CodeBlock
                      id="sdk-env-init"
                      code={`from promptlab import track
from openai import OpenAI

# API key read from PROMPTLAB_API_KEY environment variable
client = track(OpenAI())`}
                    />
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Pricing */}
            {activeSection === "pricing" && (
              <div className="space-y-8">
                <div>
                  <Badge variant="secondary" className="mb-4">
                    <Zap className="h-3 w-3 mr-1" />
                    Pricing
                  </Badge>
                  <h1 className="text-4xl font-bold mb-4">Pricing & Limits</h1>
                  <p className="text-lg text-muted-foreground">
                    Choose the plan that fits your needs. Start free, upgrade when you're ready.
                  </p>
                </div>

                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                  {[
                    {
                      name: "Free",
                      price: "$0",
                      period: "forever",
                      features: [
                        "1,000 requests/month",
                        "10 optimizations/month",
                        "Standard optimization mode",
                        "7-day data retention",
                        "Basic analytics"
                      ],
                      highlighted: false
                    },
                    {
                      name: "Premium",
                      price: "$15",
                      period: "/month",
                      features: [
                        "10,000 requests/month",
                        "50 optimizations/month",
                        "Enhanced mode with web search",
                        "Judge evaluation",
                        "30-day data retention",
                        "Email support"
                      ],
                      highlighted: false
                    },
                    {
                      name: "Pro",
                      price: "$90",
                      period: "/month",
                      features: [
                        "100,000 requests/month",
                        "Unlimited optimizations",
                        "Enhanced mode with web search",
                        "Judge eval + auto-retry",
                        "90-day data retention",
                        "A/B testing suite",
                        "Priority support"
                      ],
                      highlighted: true
                    },
                    {
                      name: "Enterprise",
                      price: "Custom",
                      period: "",
                      features: [
                        "Unlimited requests",
                        "Unlimited optimizations",
                        "Enhanced mode with web search",
                        "On-premise deployment",
                        "SSO & SAML",
                        "Dedicated support"
                      ],
                      highlighted: false
                    }
                  ].map((tier) => (
                    <Card
                      key={tier.name}
                      className={tier.highlighted ? "border-primary border-2" : ""}
                    >
                      <CardHeader>
                        <CardTitle className="flex items-center justify-between">
                          {tier.name}
                          {tier.highlighted && <Badge>Popular</Badge>}
                        </CardTitle>
                        <div>
                          <span className="text-3xl font-bold">{tier.price}</span>
                          <span className="text-muted-foreground">{tier.period}</span>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <ul className="space-y-2">
                          {tier.features.map((feature) => (
                            <li key={feature} className="flex items-start gap-2 text-sm">
                              <Check className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                              {feature}
                            </li>
                          ))}
                        </ul>
                      </CardContent>
                    </Card>
                  ))}
                </div>

                <Card>
                  <CardHeader>
                    <CardTitle>Rate Limits & Fair Use</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="text-muted-foreground">
                      All plans include reasonable rate limits to ensure fair usage:
                    </p>
                    <ul className="list-disc list-inside text-muted-foreground space-y-1">
                      <li>API requests: 100 requests per minute</li>
                      <li>Optimization requests: 10 per minute</li>
                      <li>Bulk operations: 50 per minute</li>
                    </ul>
                    <p className="text-muted-foreground">
                      Enterprise customers can request custom rate limits.
                    </p>
                  </CardContent>
                </Card>
              </div>
            )}
          </main>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t py-8 px-4 sm:px-6 lg:px-8 mt-16">
        <div className="max-w-7xl mx-auto text-center text-sm text-muted-foreground">
          <p>&copy; {new Date().getFullYear()} PromptLab. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
