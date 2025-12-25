import { Link } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  
  BarChart3,
  Sparkles,
  GitCompare,
  Shield,
  Clock,
  ArrowRight,
  Check,
  Code2,
  Lightbulb,
  Brain,
  Target,
  FileText,
  Layers,
  TrendingUp
} from "lucide-react"

const scoringCategories = [
  { name: "Clarity & Specificity", points: "0-20", description: "Clear task definition, unambiguous instructions" },
  { name: "Structure & Organization", points: "0-20", description: "XML tags, markdown, consistent formatting" },
  { name: "Role Definition", points: "0-15", description: "Specific persona with defined expertise" },
  { name: "Output Format", points: "0-15", description: "Explicit format and verbosity guidance" },
  { name: "Few-Shot Examples", points: "0-15", description: "Diverse, high-quality demonstrations" },
  { name: "Constraints & Boundaries", points: "0-10", description: "Clear scope and edge case handling" },
  { name: "Reasoning Guidance", points: "0-5", description: "Chain-of-thought instructions" },
]

const optimizationBenefits = [
  {
    icon: Brain,
    title: "Research-Backed Optimization",
    description: "Our optimizer uses 2025 best practices from OpenAI, Anthropic, and Google DeepMind research."
  },
  {
    icon: Target,
    title: "100-Point Scoring System",
    description: "Every prompt is scored across 7 categories based on proven prompt engineering principles."
  },
  {
    icon: Lightbulb,
    title: "Auto-Generated Examples",
    description: "We automatically research and generate high-quality few-shot examples for your prompts."
  },
  {
    icon: TrendingUp,
    title: "Measurable Improvements",
    description: "See exactly how your prompts improve with before/after scores and detailed breakdowns."
  }
]

const features = [
  {
    icon: Sparkles,
    title: "AI-Powered Prompt Optimization",
    description: "Transform vague prompts into precise instructions using techniques from OpenAI's GPT-5 guide, Anthropic's Claude docs, and Google's Gemini research."
  },
  {
    icon: BarChart3,
    title: "Request Logging & Analytics",
    description: "Capture every LLM API call with full request/response data, token counts, latency metrics, and cost tracking."
  },
  {
    icon: GitCompare,
    title: "A/B Testing & Comparison",
    description: "Compare prompt variations with automatic scoring to find the best performing version."
  },
  {
    icon: Shield,
    title: "Quality Scoring",
    description: "Every response is evaluated for correctness, completeness, clarity, and safety."
  },
  {
    icon: Clock,
    title: "Real-time Monitoring",
    description: "Watch your API calls in real-time with instant insights into performance."
  },
  {
    icon: Code2,
    title: "Simple SDK Integration",
    description: "Drop-in Python SDK that works with OpenAI, Anthropic, and other LLM providers."
  }
]

const pricingTiers = [
  {
    name: "Free",
    price: "$0",
    period: "forever",
    description: "Perfect for getting started",
    features: [
      "1,000 logged requests/month",
      "10 prompt optimizations/month",
      "7-day data retention",
      "Basic analytics",
      "Community support"
    ],
    cta: "Get Started",
    highlighted: false,
    plan: "free"
  },
  {
    name: "Premium",
    price: "$15",
    period: "/month",
    description: "For individual developers",
    features: [
      "10,000 logged requests/month",
      "50 prompt optimizations/month",
      "30-day data retention",
      "Advanced analytics",
      "Email support"
    ],
    cta: "Start Free Trial",
    highlighted: false,
    plan: "team"
  },
  {
    name: "Pro",
    price: "$90",
    period: "/month",
    description: "For teams & power users",
    features: [
      "100,000 logged requests/month",
      "Unlimited optimizations",
      "90-day data retention",
      "A/B testing suite",
      "Priority support"
    ],
    cta: "Start Free Trial",
    highlighted: true,
    plan: "pro"
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "",
    description: "For large organizations",
    features: [
      "Unlimited requests",
      "Unlimited optimizations",
      "On-premise deployment",
      "SSO & SAML",
      "Dedicated support"
    ],
    cta: "Contact Sales",
    highlighted: false,
    plan: "enterprise"
  }
]


export function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <img src="/clarynt_icon.jpg" alt="Clarynt" className="h-8 w-8 text-primary" />
              <span className="text-xl font-bold">PromptLab</span>
            </div>
            <div className="hidden md:flex items-center gap-8">
              <a href="#optimization" className="text-muted-foreground hover:text-foreground transition-colors">Optimization</a>
              <a href="#features" className="text-muted-foreground hover:text-foreground transition-colors">Features</a>
              <a href="#pricing" className="text-muted-foreground hover:text-foreground transition-colors">Pricing</a>
            </div>
            <div className="flex items-center gap-4">
              <Link to="/login">
                <Button variant="ghost">Sign In</Button>
              </Link>
              <Link to="/login">
                <Button>Get Started</Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <Badge className="mb-4" variant="secondary">
            <Brain className="h-3 w-3 mr-1" />
            Powered by 2025 AI Research
          </Badge>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight mb-6">
            Turn Good Prompts Into{" "}
            <span className="text-primary">Great Ones</span>
          </h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-8">
            PromptLab optimizes your LLM prompts using best practices from OpenAI, Anthropic, and Google DeepMind.
            Get measurable improvements with our 100-point scoring system and auto-generated few-shot examples.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/login">
              <Button size="lg" className="w-full sm:w-auto">
                Optimize Your First Prompt <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
            <a href="#optimization">
              <Button size="lg" variant="outline" className="w-full sm:w-auto">
                See How It Works
              </Button>
            </a>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-8 mt-16 max-w-3xl mx-auto">
            <div>
              <div className="text-3xl font-bold text-primary">+47%</div>
              <div className="text-sm text-muted-foreground">Avg. Score Improvement</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-primary">7</div>
              <div className="text-sm text-muted-foreground">Scoring Categories</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-primary">3</div>
              <div className="text-sm text-muted-foreground">AI Lab Sources</div>
            </div>
          </div>
        </div>
      </section>

      {/* Optimization Demo */}
      <section id="optimization" className="py-20 px-4 sm:px-6 lg:px-8 bg-muted/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <Badge className="mb-4" variant="secondary">
              <Sparkles className="h-3 w-3 mr-1" />
              AI-Powered Optimization
            </Badge>
            <h2 className="text-3xl font-bold mb-4">See the Transformation</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Watch how our optimizer analyzes, scores, and improves your prompts in real-time
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-8 items-start">
            {/* Before/After Demo */}
            <div className="space-y-6">
              <div className="bg-card rounded-xl border p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <FileText className="h-5 w-5 text-red-500" />
                    <span className="font-semibold">Original Prompt</span>
                  </div>
                  <Badge variant="destructive">Score: 32/100</Badge>
                </div>
                <div className="bg-red-50 dark:bg-red-950/20 p-4 rounded-lg text-sm border border-red-200 dark:border-red-800">
                  Write a summary of the article. Make it good and include the important parts.
                </div>
                <div className="mt-4 text-sm text-muted-foreground">
                  <span className="font-medium text-red-600">Issues found:</span> No role definition, vague instructions, missing output format, no examples
                </div>
              </div>

              <div className="flex justify-center">
                <div className="flex items-center gap-2 text-primary">
                  <Sparkles className="h-5 w-5 animate-pulse" />
                  <span className="font-medium">Optimizing with 2025 best practices...</span>
                </div>
              </div>

              <div className="bg-card rounded-xl border p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <FileText className="h-5 w-5 text-green-500" />
                    <span className="font-semibold">Optimized Prompt</span>
                  </div>
                  <Badge className="bg-green-100 text-green-800 hover:bg-green-100">Score: 89/100</Badge>
                </div>
                <div className="bg-green-50 dark:bg-green-950/20 p-4 rounded-lg text-sm border border-green-200 dark:border-green-800 space-y-2">
                  <p><strong>&lt;role&gt;</strong></p>
                  <p>You are an expert content analyst specializing in extracting key insights from articles.</p>
                  <p><strong>&lt;/role&gt;</strong></p>
                  <p className="mt-2"><strong>&lt;task&gt;</strong></p>
                  <p>Create a concise summary that:</p>
                  <p>- Captures the main thesis in 1-2 sentences</p>
                  <p>- Lists 3-5 key supporting points</p>
                  <p>- Notes any data or statistics cited</p>
                  <p>- Keeps total length under 150 words</p>
                  <p><strong>&lt;/task&gt;</strong></p>
                  <p className="mt-2"><strong>&lt;format&gt;</strong></p>
                  <p>Use markdown with clear headings.</p>
                  <p><strong>&lt;/format&gt;</strong></p>
                </div>
                <div className="mt-4 text-sm text-green-600">
                  <span className="font-medium">+57 points:</span> Added role, XML structure, specific requirements, output format
                </div>
              </div>
            </div>

            {/* Scoring Breakdown */}
            <div className="bg-card rounded-xl border p-6">
              <div className="flex items-center gap-2 mb-6">
                <Target className="h-5 w-5 text-primary" />
                <span className="font-semibold text-lg">100-Point Scoring Rubric</span>
              </div>
              <p className="text-sm text-muted-foreground mb-6">
                Based on 2025 research from OpenAI, Anthropic, and Google DeepMind
              </p>
              <div className="space-y-4">
                {scoringCategories.map((category) => (
                  <div key={category.name} className="flex items-start gap-3">
                    <div className="w-16 text-sm font-mono text-primary font-medium">
                      {category.points}
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-sm">{category.name}</div>
                      <div className="text-xs text-muted-foreground">{category.description}</div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-6 pt-6 border-t">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium">Total</span>
                  <span className="font-mono font-bold text-primary">100 points</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Optimization Benefits */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4">Why Our Optimizer Works</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              We don't guess - we apply proven techniques from the world's leading AI labs
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {optimizationBenefits.map((benefit) => (
              <Card key={benefit.title} className="text-center">
                <CardHeader>
                  <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mx-auto mb-4">
                    <benefit.icon className="h-6 w-6 text-primary" />
                  </div>
                  <CardTitle className="text-lg">{benefit.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription>{benefit.description}</CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Research Sources */}
          <div className="mt-16 p-8 bg-muted/30 rounded-xl">
            <div className="text-center mb-8">
              <h3 className="text-xl font-semibold mb-2">Backed by Latest Research</h3>
              <p className="text-muted-foreground">Our optimization techniques come directly from official AI lab documentation</p>
            </div>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="font-semibold mb-2">OpenAI GPT-5 Guide</div>
                <p className="text-sm text-muted-foreground">XML-based organization, clear instruction hierarchies, escape hatches for constraints</p>
              </div>
              <div className="text-center">
                <div className="font-semibold mb-2">Anthropic Claude Docs</div>
                <p className="text-sm text-muted-foreground">Specificity, chain-of-thought reasoning, thinking tags for complex tasks</p>
              </div>
              <div className="text-center">
                <div className="font-semibold mb-2">Google Gemini Research</div>
                <p className="text-sm text-muted-foreground">Few-shot examples, consistent formatting, direct and precise instructions</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Few-Shot Generation */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-muted/30">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <Badge className="mb-4" variant="secondary">
                <Lightbulb className="h-3 w-3 mr-1" />
                Automatic Example Generation
              </Badge>
              <h2 className="text-3xl font-bold mb-4">Few-Shot Examples, Automatically</h2>
              <p className="text-lg text-muted-foreground mb-6">
                Google's research shows that "prompts without few-shot examples are likely to be less effective."
                Our optimizer automatically researches and generates high-quality examples for your prompts.
              </p>
              <ul className="space-y-3">
                {[
                  "2-4 diverse examples covering different scenarios",
                  "Progressive complexity from simple to edge cases",
                  "Consistent formatting that teaches the pattern",
                  "Quality outputs that demonstrate expected results"
                ].map((item) => (
                  <li key={item} className="flex items-center gap-2">
                    <Check className="h-5 w-5 text-green-500" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="bg-card rounded-xl border p-6">
              <div className="flex items-center gap-2 mb-4">
                <Layers className="h-5 w-5 text-yellow-500" />
                <span className="font-semibold">Generated Few-Shot Examples</span>
              </div>
              <div className="space-y-4">
                <div className="p-3 bg-muted rounded-lg">
                  <div className="text-xs font-medium text-muted-foreground mb-1">Example 1 (Simple)</div>
                  <div className="text-sm">
                    <span className="text-blue-600">Input:</span> "Summarize this product review"<br/>
                    <span className="text-green-600">Output:</span> "## Summary\n**Rating:** 4/5\n**Key Points:**..."
                  </div>
                </div>
                <div className="p-3 bg-muted rounded-lg">
                  <div className="text-xs font-medium text-muted-foreground mb-1">Example 2 (Complex)</div>
                  <div className="text-sm">
                    <span className="text-blue-600">Input:</span> "Summarize this technical whitepaper"<br/>
                    <span className="text-green-600">Output:</span> "## Technical Summary\n**Abstract:**..."
                  </div>
                </div>
                <div className="p-3 bg-muted rounded-lg">
                  <div className="text-xs font-medium text-muted-foreground mb-1">Example 3 (Edge Case)</div>
                  <div className="text-sm">
                    <span className="text-blue-600">Input:</span> "Summarize this mixed-language document"<br/>
                    <span className="text-green-600">Output:</span> "## Summary (English)\n**Note:** Original..."
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4">Complete LLMOps Platform</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Beyond optimization - everything you need to build production AI applications
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature) => (
              <Card key={feature.title} className="border-2 hover:border-primary/50 transition-colors">
                <CardHeader>
                  <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                    <feature.icon className="h-6 w-6 text-primary" />
                  </div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">{feature.description}</CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-muted/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4">Get Started in Minutes</h2>
            <p className="text-xl text-muted-foreground">Simple integration with your existing LLM workflow</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="h-16 w-16 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                1
              </div>
              <h3 className="text-xl font-semibold mb-2">Paste Your Prompt</h3>
              <p className="text-muted-foreground mb-4">Enter any prompt you want to optimize</p>
              <div className="bg-card rounded-lg p-3 font-mono text-sm border">
                "Summarize this document..."
              </div>
            </div>
            <div className="text-center">
              <div className="h-16 w-16 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                2
              </div>
              <h3 className="text-xl font-semibold mb-2">Get Scored & Optimized</h3>
              <p className="text-muted-foreground mb-4">Our AI analyzes and improves it</p>
              <div className="bg-card rounded-lg p-3 text-sm border">
                <span className="text-red-500">32/100</span> → <span className="text-green-500">89/100</span>
              </div>
            </div>
            <div className="text-center">
              <div className="h-16 w-16 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                3
              </div>
              <h3 className="text-xl font-semibold mb-2">Use Better Prompts</h3>
              <p className="text-muted-foreground mb-4">Copy the optimized version with examples</p>
              <div className="bg-card rounded-lg p-3 font-mono text-sm border text-left">
                &lt;role&gt;...&lt;/role&gt;<br/>
                &lt;task&gt;...&lt;/task&gt;
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 px-4 sm:px-6 lg:px-8 bg-muted/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4">Simple, Transparent Pricing</h2>
            <p className="text-xl text-muted-foreground">Start free and scale as you grow</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {pricingTiers.map((tier) => (
              <Card
                key={tier.name}
                className={tier.highlighted ? "border-primary border-2 relative" : ""}
              >
                {tier.highlighted && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <Badge className="bg-primary">Most Popular</Badge>
                  </div>
                )}
                <CardHeader>
                  <CardTitle>{tier.name}</CardTitle>
                  <CardDescription>{tier.description}</CardDescription>
                  <div className="mt-4">
                    <span className="text-4xl font-bold">{tier.price}</span>
                    <span className="text-muted-foreground">{tier.period}</span>
                  </div>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2 mb-6">
                    {tier.features.map((feature) => (
                      <li key={feature} className="flex items-start gap-2 text-sm">
                        <Check className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                        {feature}
                      </li>
                    ))}
                  </ul>
                  <Link to="/login" className="block">
                    <Button
                      className="w-full"
                      variant={tier.highlighted ? "default" : "outline"}
                    >
                      {tier.cta}
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-primary text-primary-foreground">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to Write Better Prompts?</h2>
          <p className="text-xl opacity-90 mb-8">
            Join teams using PromptLab to build more reliable AI products with research-backed prompt optimization.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/login">
              <Button size="lg" variant="secondary">
                Start Optimizing Free <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <img src="/clarynt_icon.jpg" alt="Clarynt" className="h-6 w-6 text-primary" />
                <span className="text-lg font-bold">PromptLab</span>
              </div>
              <p className="text-sm text-muted-foreground">
                Research-backed prompt optimization for production AI applications.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="#optimization" className="hover:text-foreground">Optimization</a></li>
                <li><a href="#features" className="hover:text-foreground">Features</a></li>
                <li><a href="#pricing" className="hover:text-foreground">Pricing</a></li>
                <li><a href="#" className="hover:text-foreground">Documentation</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="#" className="hover:text-foreground">About</a></li>
                <li><a href="#" className="hover:text-foreground">Blog</a></li>
                <li><a href="#" className="hover:text-foreground">Careers</a></li>
                <li><a href="#" className="hover:text-foreground">Contact</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="#" className="hover:text-foreground">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-foreground">Terms of Service</a></li>
                <li><a href="#" className="hover:text-foreground">Security</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t mt-12 pt-8 text-center text-sm text-muted-foreground">
            <p>&copy; {new Date().getFullYear()} PromptLab. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
