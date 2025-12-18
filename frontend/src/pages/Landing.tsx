import { Link } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  Zap,
  BarChart3,
  Sparkles,
  GitCompare,
  Shield,
  Clock,
  ArrowRight,
  Check,
  Code2,
  Lightbulb
} from "lucide-react"

const features = [
  {
    icon: BarChart3,
    title: "Request Logging & Analytics",
    description: "Automatically capture every LLM API call with full request/response data, token counts, latency metrics, and costs."
  },
  {
    icon: Sparkles,
    title: "AI-Powered Prompt Optimization",
    description: "Our intelligent optimizer analyzes your prompts and suggests improvements using proven prompt engineering techniques."
  },
  {
    icon: GitCompare,
    title: "A/B Testing & Comparison",
    description: "Compare prompt variations side-by-side with automatic scoring to find the best performing version."
  },
  {
    icon: Shield,
    title: "Quality Scoring",
    description: "Every response is automatically evaluated for quality, relevance, and adherence to instructions."
  },
  {
    icon: Clock,
    title: "Real-time Monitoring",
    description: "Watch your API calls in real-time with instant insights into performance and potential issues."
  },
  {
    icon: Code2,
    title: "Simple SDK Integration",
    description: "Drop-in Python SDK that works with OpenAI, Anthropic, and other major LLM providers."
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
      "7-day data retention",
      "Basic analytics",
      "1 team member",
      "Community support"
    ],
    cta: "Get Started",
    highlighted: false
  },
  {
    name: "Pro",
    price: "$99",
    period: "/month",
    description: "For growing teams",
    features: [
      "50,000 logged requests/month",
      "90-day data retention",
      "Advanced analytics & exports",
      "Prompt optimization (100/month)",
      "5 team members",
      "Email support"
    ],
    cta: "Start Free Trial",
    highlighted: true
  },
  {
    name: "Team",
    price: "$299",
    period: "/month",
    description: "For serious AI development",
    features: [
      "500,000 logged requests/month",
      "1-year data retention",
      "Unlimited prompt optimizations",
      "A/B testing suite",
      "Unlimited team members",
      "Priority support",
      "Custom integrations"
    ],
    cta: "Start Free Trial",
    highlighted: false
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "",
    description: "For large organizations",
    features: [
      "Unlimited requests",
      "Unlimited data retention",
      "On-premise deployment",
      "SSO & SAML",
      "Dedicated support",
      "Custom SLAs",
      "Training & onboarding"
    ],
    cta: "Contact Sales",
    highlighted: false
  }
]

const testimonials = [
  {
    quote: "PromptLab helped us reduce our LLM costs by 40% while improving output quality.",
    author: "Sarah Chen",
    role: "ML Engineer, TechCorp"
  },
  {
    quote: "The prompt optimizer is a game-changer. What used to take hours of iteration now happens in seconds.",
    author: "Michael Rodriguez",
    role: "Founder, AI Startup"
  },
  {
    quote: "Finally, visibility into our LLM operations. Can't imagine building AI products without it.",
    author: "Emily Watson",
    role: "CTO, DataFlow Inc"
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
              <Zap className="h-8 w-8 text-primary" />
              <span className="text-xl font-bold">PromptLab</span>
            </div>
            <div className="hidden md:flex items-center gap-8">
              <a href="#features" className="text-muted-foreground hover:text-foreground transition-colors">Features</a>
              <a href="#pricing" className="text-muted-foreground hover:text-foreground transition-colors">Pricing</a>
              <a href="#testimonials" className="text-muted-foreground hover:text-foreground transition-colors">Testimonials</a>
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
            Now with AI-Powered Optimization
          </Badge>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight mb-6">
            Ship Better AI Products,{" "}
            <span className="text-primary">Faster</span>
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-8">
            PromptLab is your complete platform for logging, monitoring, and optimizing LLM API calls.
            Get visibility into every request and use AI to improve your prompts automatically.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/login">
              <Button size="lg" className="w-full sm:w-auto">
                Start Free <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
            <a href="#features">
              <Button size="lg" variant="outline" className="w-full sm:w-auto">
                See Features
              </Button>
            </a>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-8 mt-16 max-w-3xl mx-auto">
            <div>
              <div className="text-3xl font-bold text-primary">10M+</div>
              <div className="text-sm text-muted-foreground">Requests Logged</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-primary">40%</div>
              <div className="text-sm text-muted-foreground">Avg. Cost Reduction</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-primary">500+</div>
              <div className="text-sm text-muted-foreground">Teams Using PromptLab</div>
            </div>
          </div>
        </div>
      </section>

      {/* Demo Preview */}
      <section className="py-12 px-4 sm:px-6 lg:px-8 bg-muted/30">
        <div className="max-w-6xl mx-auto">
          <div className="rounded-xl border bg-card shadow-2xl overflow-hidden">
            <div className="bg-muted px-4 py-2 flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <span className="ml-4 text-sm text-muted-foreground">PromptLab Dashboard</span>
            </div>
            <div className="p-8 space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold">Recent Requests</h3>
                  <p className="text-sm text-muted-foreground">Real-time view of your LLM API calls</p>
                </div>
                <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                  <span className="w-2 h-2 rounded-full bg-green-500 mr-2 animate-pulse"></span>
                  Live
                </Badge>
              </div>
              <div className="space-y-3">
                {[
                  { model: "gpt-4", tokens: 1250, latency: "1.2s", score: 8.5 },
                  { model: "claude-3", tokens: 890, latency: "0.8s", score: 9.2 },
                  { model: "gpt-4", tokens: 2100, latency: "2.1s", score: 7.8 },
                ].map((req, i) => (
                  <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                    <div className="flex items-center gap-4">
                      <Badge variant="secondary">{req.model}</Badge>
                      <span className="text-sm">{req.tokens} tokens</span>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className="text-sm text-muted-foreground">{req.latency}</span>
                      <Badge className={req.score >= 8 ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"}>
                        Score: {req.score}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4">Everything You Need to Master LLM Operations</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              From logging to optimization, PromptLab gives you complete visibility and control over your AI applications.
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
              <h3 className="text-xl font-semibold mb-2">Install the SDK</h3>
              <p className="text-muted-foreground mb-4">Add our Python package with a single command</p>
              <div className="bg-card rounded-lg p-3 font-mono text-sm border">
                pip install promptlab
              </div>
            </div>
            <div className="text-center">
              <div className="h-16 w-16 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                2
              </div>
              <h3 className="text-xl font-semibold mb-2">Configure Your API Key</h3>
              <p className="text-muted-foreground mb-4">Initialize with your PromptLab API key</p>
              <div className="bg-card rounded-lg p-3 font-mono text-sm border text-left">
                <code>
                  <span className="text-blue-600">from</span> promptlab <span className="text-blue-600">import</span> PromptLab<br/>
                  pl = PromptLab(api_key=<span className="text-green-600">"pl_..."</span>)
                </code>
              </div>
            </div>
            <div className="text-center">
              <div className="h-16 w-16 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                3
              </div>
              <h3 className="text-xl font-semibold mb-2">Start Logging</h3>
              <p className="text-muted-foreground mb-4">Wrap your API calls and start getting insights</p>
              <div className="bg-card rounded-lg p-3 font-mono text-sm border text-left">
                <code>
                  response = pl.chat(<br/>
                  &nbsp;&nbsp;model=<span className="text-green-600">"gpt-4"</span>,<br/>
                  &nbsp;&nbsp;messages=[...]<br/>
                  )
                </code>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Prompt Optimization Highlight */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <Badge className="mb-4" variant="secondary">
                <Sparkles className="h-3 w-3 mr-1" />
                AI-Powered
              </Badge>
              <h2 className="text-3xl font-bold mb-4">Optimize Prompts with AI</h2>
              <p className="text-lg text-muted-foreground mb-6">
                Our intelligent prompt optimizer analyzes your prompts and suggests improvements
                based on proven prompt engineering techniques. Get better results without manual trial and error.
              </p>
              <ul className="space-y-3">
                {[
                  "Automatic issue detection and scoring",
                  "Specific, actionable improvement suggestions",
                  "Side-by-side comparison with score changes",
                  "Save and track your optimization history"
                ].map((item) => (
                  <li key={item} className="flex items-center gap-2">
                    <Check className="h-5 w-5 text-green-500" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
              <Link to="/login" className="mt-8 inline-block">
                <Button>
                  Try Prompt Optimizer <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>
            <div className="bg-card rounded-xl border p-6 space-y-4">
              <div className="flex items-center gap-2 mb-4">
                <Lightbulb className="h-5 w-5 text-yellow-500" />
                <span className="font-semibold">Optimization Example</span>
              </div>
              <div>
                <div className="text-sm font-medium text-muted-foreground mb-2">Original Prompt</div>
                <div className="bg-muted p-3 rounded-lg text-sm">
                  Write me a summary of this document.
                </div>
                <div className="text-xs text-muted-foreground mt-1">Score: 4.2/10</div>
              </div>
              <div className="flex justify-center">
                <ArrowRight className="h-6 w-6 text-primary" />
              </div>
              <div>
                <div className="text-sm font-medium text-muted-foreground mb-2">Optimized Prompt</div>
                <div className="bg-green-50 dark:bg-green-950/20 p-3 rounded-lg text-sm border border-green-200">
                  You are an expert technical writer. Create a concise summary of the following document that:
                  - Captures the main thesis and key arguments
                  - Highlights important data points
                  - Uses bullet points for clarity
                  - Keeps the summary under 200 words
                </div>
                <div className="text-xs text-green-600 mt-1">Score: 9.1/10 (+4.9 improvement)</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section id="testimonials" className="py-20 px-4 sm:px-6 lg:px-8 bg-muted/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4">Loved by AI Teams</h2>
            <p className="text-xl text-muted-foreground">See what developers are saying about PromptLab</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial) => (
              <Card key={testimonial.author}>
                <CardContent className="pt-6">
                  <p className="text-lg mb-4">"{testimonial.quote}"</p>
                  <div>
                    <div className="font-semibold">{testimonial.author}</div>
                    <div className="text-sm text-muted-foreground">{testimonial.role}</div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 px-4 sm:px-6 lg:px-8">
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
          <h2 className="text-3xl font-bold mb-4">Ready to Optimize Your LLM Operations?</h2>
          <p className="text-xl opacity-90 mb-8">
            Join hundreds of teams using PromptLab to build better AI products.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/login">
              <Button size="lg" variant="secondary">
                Start Free Today <ArrowRight className="ml-2 h-4 w-4" />
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
                <Zap className="h-6 w-6 text-primary" />
                <span className="text-lg font-bold">PromptLab</span>
              </div>
              <p className="text-sm text-muted-foreground">
                The complete platform for LLM logging, monitoring, and optimization.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="#features" className="hover:text-foreground">Features</a></li>
                <li><a href="#pricing" className="hover:text-foreground">Pricing</a></li>
                <li><a href="#" className="hover:text-foreground">Documentation</a></li>
                <li><a href="#" className="hover:text-foreground">API Reference</a></li>
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
