import { Link } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { VideoComparisonDemo } from "@/components/VideoComparisonDemo"
import {

  BarChart3,
  Sparkles,
  GitCompare,
  Shield,
  ArrowRight,
  Check,
  Code2,
  Target,
  Play,
  ChevronDown,
  Building2,
  Star
} from "lucide-react"
import { useState } from "react"

// ============================================================================
// CONVERSION-OPTIMIZED LANDING PAGE V2
// Design principles from Figma & Uber:
// - Single clear CTA above the fold
// - Problem-agitation-solution structure
// - Strong social proof throughout
// - Reduce cognitive load with focused messaging
// - Trust signals and objection handling
// ============================================================================

// Pricing tiers
const pricingTiers = [
  {
    name: "Free",
    monthlyPrice: "$0",
    yearlyPrice: "$0",
    period: "forever",
    description: "Start optimizing today",
    features: [
      "1,000 logged requests/month",
      "10 prompt optimizations/month",
      "Standard optimization mode",
      "7-day data retention",
      "Basic analytics"
    ],
    cta: "Start Free",
    highlighted: false
  },
  {
    name: "Premium",
    monthlyPrice: "$15",
    yearlyPrice: "$12",
    period: "/month",
    yearlyTotal: "$144/year",
    savings: "Save $36/year",
    description: "For individual developers",
    features: [
      "10,000 logged requests/month",
      "50 prompt optimizations/month",
      "Enhanced mode with web search",
      "Judge evaluation before return",
      "File upload for context",
      "30-day data retention",
      "Email support"
    ],
    cta: "Start Free Trial",
    highlighted: false
  },
  {
    name: "Pro",
    monthlyPrice: "$90",
    yearlyPrice: "$75",
    period: "/month",
    yearlyTotal: "$900/year",
    savings: "Save $180/year",
    description: "For teams & power users",
    features: [
      "100,000 logged requests/month",
      "Unlimited optimizations",
      "Enhanced mode with web search",
      "Judge evaluation + auto-retry",
      "File upload for context",
      "90-day data retention",
      "A/B testing suite",
      "Priority support"
    ],
    cta: "Start Free Trial",
    highlighted: false
  },
  {
    name: "Enterprise",
    monthlyPrice: "Custom",
    yearlyPrice: "Custom",
    period: "",
    description: "For large organizations",
    features: [
      "Unlimited requests",
      "Unlimited optimizations",
      "Enhanced mode with web search",
      "On-premise deployment",
      "SSO & SAML",
      "Dedicated support"
    ],
    cta: "Contact Sales",
    highlighted: false
  }
]

// FAQ items for objection handling
const faqItems = [
  {
    question: "How is this different from just using ChatGPT to improve my prompts?",
    answer: "Clarynt uses a research-backed 100-point scoring system based on official guides from OpenAI, Anthropic, and Google DeepMind. Unlike generic AI suggestions, we apply specific, measurable criteria and automatically generate few-shot examples - something you can't easily do manually."
  },
  {
    question: "How long does it take to integrate?",
    answer: "Most teams are up and running in under 15 minutes. Our Python SDK wraps your existing OpenAI client with a single line of code, and the web optimizer requires no integration at all."
  },
  {
    question: "What if it doesn't improve my prompts?",
    answer: "Start with our free tier - 10 optimizations per month, no credit card required. If you don't see measurable improvements in your prompt scores, you've lost nothing. Most users see 40-60 point improvements on their first optimization."
  },
  {
    question: "Is my data secure?",
    answer: "Yes. All data is encrypted in transit and at rest. Enterprise customers can use on-premise deployment. We never use your prompts to train models or share them with third parties."
  }
]

// Platform features
const platformFeatures = [
  {
    icon: Sparkles,
    title: "AI-Powered Optimization",
    description: "Transform vague prompts into precise instructions using 2025 best practices from OpenAI, Anthropic, and Google."
  },
  {
    icon: Target,
    title: "Web-Enhanced Examples",
    description: "Paid plans use real-time web search to find grounded few-shot examples from documentation and GitHub."
  },
  {
    icon: BarChart3,
    title: "Request Logging",
    description: "Capture every LLM API call with full request/response data, token counts, and latency metrics."
  },
  {
    icon: GitCompare,
    title: "A/B Testing",
    description: "Compare prompt variations side-by-side with automatic scoring to find the best performer."
  },
  {
    icon: Shield,
    title: "Judge Evaluation",
    description: "AI Judge evaluates optimized prompts before returning, detecting regressions and ensuring quality."
  },
  {
    icon: Code2,
    title: "Simple SDK",
    description: "Drop-in Python SDK that works with OpenAI, Anthropic, and other providers."
  }
]

export function LandingPageV2() {
  const [openFaq, setOpenFaq] = useState<number | null>(null)

  return (
    <div className="min-h-screen bg-background">
      {/* ================================================================
          NAVIGATION - Clean, minimal (Figma-style)
          ================================================================ */}
      <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <img src="/clarynt_icon.jpg" alt="Clarynt" className="h-8 w-8" />
              <span className="text-xl font-bold">Clarynt</span>
            </div>
            <div className="hidden md:flex items-center gap-8">
              <a href="#how-it-works" className="text-muted-foreground hover:text-foreground transition-colors">How it works</a>
              <a href="#features" className="text-muted-foreground hover:text-foreground transition-colors">Features</a>
              <a href="#pricing" className="text-muted-foreground hover:text-foreground transition-colors">Pricing</a>
              <Link to="/docs" className="text-muted-foreground hover:text-foreground transition-colors">Docs</Link>
              <Link to="/education" className="text-muted-foreground hover:text-foreground transition-colors">Learn</Link>
            </div>
            <div className="flex items-center gap-4">
              <Link to="/login">
                <Button variant="ghost">Sign In</Button>
              </Link>
              <Link to="/login">
                <Button>Get Started Free</Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* ================================================================
          HERO SECTION - Single CTA, Problem-focused (Uber-style)
          Key: One clear value prop, one primary action
          ================================================================ */}
      <section className="py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-5xl mx-auto text-center">
          {/* Main headline - Problem/Solution in one */}
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight mb-6">
            Creative Prompts
            <br />
            <span className="text-primary">That Actually Work.</span>
          </h1>

          {/* Value prop - Specific, measurable benefit */}
          <p className="text-xl sm:text-2xl text-muted-foreground max-w-3xl mx-auto mb-8">
            Stop wasting generations on bad prompts. Our AI optimizer creates perfect prompts for Midjourney, Stable Diffusion, DALL-E, Runway, and more.
          </p>

          {/* Model logos */}
          <div className="flex flex-wrap justify-center gap-4 mb-10 text-sm text-muted-foreground">
            <span className="px-3 py-1 bg-muted rounded-full">Midjourney</span>
            <span className="px-3 py-1 bg-muted rounded-full">Stable Diffusion</span>
            <span className="px-3 py-1 bg-muted rounded-full">DALL-E 3</span>
            <span className="px-3 py-1 bg-muted rounded-full">Runway</span>
            <span className="px-3 py-1 bg-muted rounded-full">Flux</span>
          </div>

          {/* Single primary CTA */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-8">
            <Link to="/login">
              <Button size="lg" className="text-lg px-8 py-6 h-auto">
                Create Your First Prompt
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          </div>

          {/* Risk reversal */}
          <p className="text-sm text-muted-foreground">
            No credit card required. 10 free optimizations per month.
          </p>
        </div>
      </section>

      {/* ================================================================
          SOLUTION DEMO - Before/After transformation
          Key: Visual proof of value
          ================================================================ */}
      <section id="how-it-works" className="py-24 px-4 sm:px-6 lg:px-8 bg-muted/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <Badge className="mb-4" variant="secondary">
              <Sparkles className="h-3 w-3 mr-1" />
              The Solution
            </Badge>
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              See the Transformation in Seconds
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Paste any prompt and watch it transform from vague to precise
            </p>
          </div>

          {/* Video Comparison Demo */}
          <VideoComparisonDemo />

          {/* CTA after demo */}
          <div className="text-center mt-12">
            <Link to="/login">
              <Button size="lg" className="text-lg px-8">
                <Play className="mr-2 h-5 w-5" />
                Try It Yourself
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* ================================================================
          3-STEP PROCESS - Simple, clear steps
          ================================================================ */}
      <section className="py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Three Steps to Better Prompts
            </h2>
            <p className="text-xl text-muted-foreground">
              No complex setup. No learning curve.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-12 max-w-5xl mx-auto">
            <div className="text-center">
              <div className="h-20 w-20 rounded-2xl bg-primary/10 flex items-center justify-center text-3xl font-bold text-primary mx-auto mb-6">
                1
              </div>
              <h3 className="text-xl font-semibold mb-3">Paste Your Prompt</h3>
              <p className="text-muted-foreground">
                Enter any prompt - from simple queries to complex multi-step instructions.
              </p>
            </div>

            <div className="text-center">
              <div className="h-20 w-20 rounded-2xl bg-primary/10 flex items-center justify-center text-3xl font-bold text-primary mx-auto mb-6">
                2
              </div>
              <h3 className="text-xl font-semibold mb-3">Get Your Score</h3>
              <p className="text-muted-foreground">
                Our AI scores your prompt across 7 research-backed categories and shows improvement areas.
              </p>
            </div>

            <div className="text-center">
              <div className="h-20 w-20 rounded-2xl bg-primary/10 flex items-center justify-center text-3xl font-bold text-primary mx-auto mb-6">
                3
              </div>
              <h3 className="text-xl font-semibold mb-3">Use the Optimized Version</h3>
              <p className="text-muted-foreground">
                Copy the optimized prompt with auto-generated few-shot examples and structure.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ================================================================
          WHY PROMPT QUALITY MATTERS - Research validation
          ================================================================ */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 bg-muted/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <Badge className="mb-4" variant="secondary">
              <Target className="h-3 w-3 mr-1" />
              The Research Is Clear
            </Badge>
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Your Prompts Are Holding You Back
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Studies from Harvard and Google show that how you ask is just as important as what you ask.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto mb-10">
            <Card className="border-2">
              <CardContent className="pt-6">
                <div className="text-red-500 font-semibold mb-3">The Problem</div>
                <p className="text-lg font-medium mb-2">
                  Vague prompts give vague answers
                </p>
                <p className="text-sm text-muted-foreground">
                  Harvard researchers found that people using AI without prompt training actually produced <span className="font-semibold text-foreground">worse work</span> than not using AI at all. The AI gave confident but wrong answers.
                </p>
              </CardContent>
            </Card>

            <Card className="border-2 border-primary">
              <CardContent className="pt-6">
                <div className="text-primary font-semibold mb-3">The Solution</div>
                <p className="text-lg font-medium mb-2">
                  Show the AI what you want
                </p>
                <p className="text-sm text-muted-foreground">
                  Adding just 2-3 examples of good output cuts errors in half. That's why Clarynt automatically generates relevant examples for every prompt you optimize.
                </p>
              </CardContent>
            </Card>

            <Card className="border-2">
              <CardContent className="pt-6">
                <div className="text-green-500 font-semibold mb-3">The Result</div>
                <p className="text-lg font-medium mb-2">
                  AI that actually follows instructions
                </p>
                <p className="text-sm text-muted-foreground">
                  Structured prompts with clear roles, examples, and constraints get dramatically better results. The same AI model, completely different output.
                </p>
              </CardContent>
            </Card>
          </div>

          <div className="text-center">
            <Link to="/education" className="text-primary hover:underline inline-flex items-center gap-1">
              See the research and learn best practices <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* ================================================================
          FEATURES GRID - Platform capabilities
          ================================================================ */}
      <section id="features" className="py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <Badge className="mb-4" variant="secondary">
              <Building2 className="h-3 w-3 mr-1" />
              Platform Features
            </Badge>
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Everything You Need for Production AI
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Beyond optimization - a complete LLMOps platform
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {platformFeatures.map((feature) => (
              <Card key={feature.title} className="hover:border-primary/50 transition-colors">
                <CardHeader>
                  <div className="h-12 w-12 rounded-xl bg-primary/10 flex items-center justify-center mb-4">
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

      {/* ================================================================
          SCORING SYSTEM - Credibility through methodology
          ================================================================ */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 bg-muted/30">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <Badge className="mb-4" variant="secondary">
                <Target className="h-3 w-3 mr-1" />
                Research-Backed
              </Badge>
              <h2 className="text-3xl sm:text-4xl font-bold mb-6">
                100-Point Scoring System
              </h2>
              <p className="text-lg text-muted-foreground mb-8">
                Every prompt is scored across 7 categories derived from official documentation
                and research papers from OpenAI, Anthropic, and Google DeepMind.
              </p>

              <div className="space-y-4">
                {[
                  { name: "Clarity & Specificity", points: "20", color: "bg-blue-500" },
                  { name: "Structure & Organization", points: "20", color: "bg-purple-500" },
                  { name: "Role Definition", points: "15", color: "bg-green-500" },
                  { name: "Output Format", points: "15", color: "bg-yellow-500" },
                  { name: "Few-Shot Examples", points: "15", color: "bg-orange-500" },
                  { name: "Constraints & Boundaries", points: "10", color: "bg-red-500" },
                  { name: "Reasoning Guidance", points: "5", color: "bg-pink-500" }
                ].map((category) => (
                  <div key={category.name} className="flex items-center gap-4">
                    <div className={`h-3 w-3 rounded-full ${category.color}`} />
                    <span className="flex-1">{category.name}</span>
                    <span className="font-mono font-semibold text-primary">{category.points} pts</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-card rounded-2xl border p-8">
              <div className="text-center mb-6">
                <div className="text-6xl font-bold text-primary mb-2">87</div>
                <div className="text-muted-foreground">Average optimized score</div>
              </div>
              <div className="grid grid-cols-3 gap-4 text-center">
                <div className="p-4 bg-muted/50 rounded-xl">
                  <div className="text-2xl font-bold text-primary">+47%</div>
                  <div className="text-xs text-muted-foreground">Avg. Improvement</div>
                </div>
                <div className="p-4 bg-muted/50 rounded-xl">
                  <div className="text-2xl font-bold text-primary">3</div>
                  <div className="text-xs text-muted-foreground">AI Lab Sources</div>
                </div>
                <div className="p-4 bg-muted/50 rounded-xl">
                  <div className="text-2xl font-bold text-primary">7</div>
                  <div className="text-xs text-muted-foreground">Score Categories</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ================================================================
          PRICING - Clear, transparent (Uber-style simplicity)
          ================================================================ */}
      <section id="pricing" className="py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Simple, Transparent Pricing
            </h2>
            <p className="text-xl text-muted-foreground">
              Start free. Upgrade when you need more.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {pricingTiers.map((tier) => (
              <Card
                key={tier.name}
                className={tier.highlighted ? "border-primary border-2 relative scale-105" : ""}
              >
                {tier.highlighted && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                    <Badge className="bg-primary">
                      <Star className="h-3 w-3 mr-1" />
                      Most Popular
                    </Badge>
                  </div>
                )}
                <CardHeader>
                  <CardTitle>{tier.name}</CardTitle>
                  <CardDescription>{tier.description}</CardDescription>
                  <div className="mt-4">
                    <span className="text-4xl font-bold">{tier.monthlyPrice}</span>
                    <span className="text-muted-foreground">{tier.period}</span>
                  </div>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3 mb-6">
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

      {/* ================================================================
          FAQ - Objection handling
          ================================================================ */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 bg-muted/30">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Frequently Asked Questions
            </h2>
          </div>

          <div className="space-y-4">
            {faqItems.map((faq, i) => (
              <div
                key={i}
                className="bg-card border rounded-xl overflow-hidden"
              >
                <button
                  className="w-full p-6 text-left flex items-center justify-between"
                  onClick={() => setOpenFaq(openFaq === i ? null : i)}
                >
                  <span className="font-semibold pr-4">{faq.question}</span>
                  <ChevronDown className={`h-5 w-5 text-muted-foreground transition-transform ${openFaq === i ? "rotate-180" : ""}`} />
                </button>
                {openFaq === i && (
                  <div className="px-6 pb-6 text-muted-foreground">
                    {faq.answer}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ================================================================
          FINAL CTA - Strong close
          ================================================================ */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 bg-primary text-primary-foreground">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-bold mb-6">
            Ready to Write Better Prompts?
          </h2>
          <p className="text-xl opacity-90 mb-8">
            Start building more reliable AI products with research-backed prompt optimization.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link to="/login">
              <Button size="lg" variant="secondary" className="text-lg px-8">
                Start Optimizing Free
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          </div>
          <p className="text-sm opacity-70 mt-4">
            No credit card required. 10 free optimizations per month.
          </p>
        </div>
      </section>

      {/* ================================================================
          FOOTER
          ================================================================ */}
      <footer className="border-t py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <img src="/clarynt_icon.jpg" alt="Clarynt" className="h-6 w-6" />
                <span className="text-lg font-bold">Clarynt</span>
              </div>
              <p className="text-sm text-muted-foreground">
                Research-backed prompt optimization for production AI applications.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="#how-it-works" className="hover:text-foreground">How it works</a></li>
                <li><a href="#features" className="hover:text-foreground">Features</a></li>
                <li><a href="#pricing" className="hover:text-foreground">Pricing</a></li>
                <li><Link to="/docs" className="hover:text-foreground">Documentation</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Learn</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><Link to="/education" className="hover:text-foreground">Best Practices</Link></li>
                <li><Link to="/education#privacy" className="hover:text-foreground">Privacy Guidelines</Link></li>
                <li><Link to="/docs#sdk" className="hover:text-foreground">Python SDK</Link></li>
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
            <p>&copy; {new Date().getFullYear()} Clarynt. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
