import { Link } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { AgencyDemo } from "@/components/AgencyDemo"
import {
  ArrowRight,
  Check,
  Code2,
  ChevronDown,
  Star,
  FileQuestion,
  Sparkles,
  Scale,
  Zap,
  Settings,
  BarChart3,
} from "lucide-react"
import { useState } from "react"

// ============================================================================
// AGENCY-FOCUSED LANDING PAGE
// Repositioned messaging: "ad-ready images in fewer generations"
// Clarifying Questions as the centerpiece
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
      "Basic analytics",
    ],
    cta: "Get Started Free",
    highlighted: false,
  },
  {
    name: "Premium",
    monthlyPrice: "$15",
    yearlyPrice: "$12",
    period: "/month",
    yearlyTotal: "$144/year",
    savings: "Save $36/year",
    description: "For individual creators",
    features: [
      "10,000 logged requests/month",
      "50 prompt optimizations/month",
      "Enhanced mode with web search",
      "Judge evaluation before return",
      "File upload for context",
      "30-day data retention",
      "Email support",
    ],
    cta: "Start Free Trial",
    highlighted: false,
  },
  {
    name: "Pro",
    monthlyPrice: "$90",
    yearlyPrice: "$75",
    period: "/month",
    yearlyTotal: "$900/year",
    savings: "Save $180/year",
    description: "For agencies & studios",
    features: [
      "100,000 logged requests/month",
      "Unlimited optimizations",
      "Enhanced mode with web search",
      "Judge evaluation + auto-retry",
      "File upload for context",
      "90-day data retention",
      "A/B testing suite",
      "Priority support",
    ],
    cta: "Start Free Trial",
    highlighted: true,
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
      "Dedicated support",
    ],
    cta: "Contact Sales",
    highlighted: false,
  },
]

// FAQ items - agency-focused objection handling
const faqItems = [
  {
    question: "How is this different from just using ChatGPT?",
    answer:
      "Clayrnt is built for repeatable output quality across a team. It asks targeted questions, applies a consistent scoring rubric, and produces a structured production prompt with constraints and negatives to reduce model guessing. The result is fewer failed generations and a higher first-pass usable rate.",
  },
  {
    question: "How long does it take to start?",
    answer:
      "No integration required. Paste what you want, answer questions, and copy the production prompt in minutes. API and SDK workflows are optional.",
  },
  {
    question: "What if it doesn't help?",
    answer:
      "Then do not keep it. The goal is measurable: fewer generations to reach usable outputs and closer matches to what you asked for.",
  },
  {
    question: "Is my data secure?",
    answer:
      "By default we store only what is needed to provide the service. You control retention in settings. If you need custom retention or enterprise controls, contact us.",
  },
]

// Top 3 agency-focused features
const agencyFeatures = [
  {
    icon: Zap,
    title: "Requirements → Production Prompt",
    description:
      "Paste what you want. Get back a precise, structured prompt with constraints and negatives that makes the model stop guessing.",
  },
  {
    icon: FileQuestion,
    title: "Clarifying Questions",
    description:
      "Clayrnt asks targeted questions to capture details you'd forget to specify. Container type? Lighting? What must not appear? Every answer tightens the output.",
  },
  {
    icon: Scale,
    title: "Judge Evaluation",
    description:
      "An AI Judge scores the prompt against your requirements before you run it. Know if it will work before wasting generations.",
  },
]

// Developer features (lower section)
const developerFeatures = [
  {
    icon: Code2,
    title: "Python SDK",
    description:
      "Drop-in SDK that wraps your existing OpenAI client. Automatic logging and optimization with one line of code.",
  },
  {
    icon: BarChart3,
    title: "Request Logging",
    description:
      "Capture every API call with full request/response data, token counts, and latency metrics for debugging.",
  },
  {
    icon: Settings,
    title: "A/B Testing",
    description:
      "Compare prompt variations side-by-side with automatic scoring to find the best performer.",
  },
]

export function LandingPageV2() {
  const [openFaq, setOpenFaq] = useState<number | null>(null)

  return (
    <div className="min-h-screen bg-background">
      {/* ================================================================
          NAVIGATION
          ================================================================ */}
      <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <img src="/clarynt_icon.jpg" alt="Clayrnt" className="h-8 w-8" />
              <span className="text-xl font-bold">Clayrnt</span>
            </div>
            <div className="hidden md:flex items-center gap-8">
              <a
                href="#how-it-works"
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                How it works
              </a>
              <a
                href="#features"
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                Features
              </a>
              <a
                href="#pricing"
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                Pricing
              </a>
              <Link
                to="/docs"
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                Docs
              </Link>
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
          HERO SECTION - Agency-focused value prop
          ================================================================ */}
      <section className="py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-5xl mx-auto text-center">
          {/* Main headline */}
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight mb-6">
            Get ad-ready images
            <br />
            <span className="text-primary">in fewer generations.</span>
          </h1>

          {/* Value prop */}
          <p className="text-xl sm:text-2xl text-muted-foreground max-w-3xl mx-auto mb-8">
            Paste what you want. Clayrnt asks a few quick questions, then gives you a prompt that
            makes the model stop guessing.
          </p>

          {/* Model compatibility */}
          <div className="flex flex-wrap justify-center gap-4 mb-10 text-sm text-muted-foreground">
            <span className="px-3 py-1 bg-muted rounded-full">Midjourney</span>
            <span className="px-3 py-1 bg-muted rounded-full">Stable Diffusion</span>
            <span className="px-3 py-1 bg-muted rounded-full">DALL-E 3</span>
            <span className="px-3 py-1 bg-muted rounded-full">Runway</span>
            <span className="px-3 py-1 bg-muted rounded-full">Flux</span>
          </div>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-6">
            <Link to="/login">
              <Button size="lg" className="text-lg px-8 py-6 h-auto">
                Run a 7-day agency pilot
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <Link to="/login">
              <Button variant="outline" size="lg" className="text-lg px-8 py-6 h-auto">
                Get Started Free
              </Button>
            </Link>
          </div>

          {/* Small note */}
          <p className="text-sm text-muted-foreground">
            Works with any model. Preset available for Gemini Nano Banana Pro.
          </p>
        </div>
      </section>

      {/* ================================================================
          DEMO SECTION - Before/Questions/After animation
          ================================================================ */}
      <section id="how-it-works" className="py-24 px-4 sm:px-6 lg:px-8 bg-muted/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <Badge className="mb-4" variant="secondary">
              <Sparkles className="h-3 w-3 mr-1" />
              See It Work
            </Badge>
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">Watch the model stop guessing</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Same model. Same settings. Clayrnt just makes the instructions specific.
            </p>
          </div>

          {/* Agency Demo Component */}
          <AgencyDemo />

          {/* CTA after demo */}
          <div className="text-center mt-12">
            <Link to="/login">
              <Button size="lg" className="text-lg px-8">
                Try It Yourself
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* ================================================================
          3-STEP PROCESS - Simple steps
          ================================================================ */}
      <section className="py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">Three steps to usable outputs</h2>
            <p className="text-xl text-muted-foreground">No integration. No learning curve.</p>
          </div>

          <div className="grid md:grid-cols-3 gap-12 max-w-5xl mx-auto">
            <div className="text-center">
              <div className="h-20 w-20 rounded-2xl bg-primary/10 flex items-center justify-center text-3xl font-bold text-primary mx-auto mb-6">
                1
              </div>
              <h3 className="text-xl font-semibold mb-3">Paste what you want</h3>
              <p className="text-muted-foreground">
                Describe the image, video, or asset you need in plain language.
              </p>
            </div>

            <div className="text-center">
              <div className="h-20 w-20 rounded-2xl bg-primary/10 flex items-center justify-center text-3xl font-bold text-primary mx-auto mb-6">
                2
              </div>
              <h3 className="text-xl font-semibold mb-3">Answer a few questions</h3>
              <p className="text-muted-foreground">
                Clayrnt asks targeted questions to capture the details that matter.
              </p>
            </div>

            <div className="text-center">
              <div className="h-20 w-20 rounded-2xl bg-primary/10 flex items-center justify-center text-3xl font-bold text-primary mx-auto mb-6">
                3
              </div>
              <h3 className="text-xl font-semibold mb-3">Copy the production prompt</h3>
              <p className="text-muted-foreground">
                Get a structured prompt with constraints that makes the model stop guessing.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ================================================================
          FEATURES - Agency-focused (top) + Developer (lower)
          ================================================================ */}
      <section id="features" className="py-24 px-4 sm:px-6 lg:px-8 bg-muted/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <Badge className="mb-4" variant="secondary">
              <Zap className="h-3 w-3 mr-1" />
              For Teams
            </Badge>
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">Built for teams shipping volume</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Standardize how your team gets usable outputs fast.
            </p>
          </div>

          {/* Agency features - prominent */}
          <div className="grid md:grid-cols-3 gap-8 mb-16">
            {agencyFeatures.map((feature) => (
              <Card
                key={feature.title}
                className="hover:border-primary/50 transition-colors border-2"
              >
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

          {/* Developer features - de-emphasized */}
          <div className="border-t pt-16">
            <div className="text-center mb-12">
              <h3 className="text-xl font-semibold text-muted-foreground mb-2">For Developers</h3>
              <p className="text-muted-foreground">
                Optional API and SDK integrations for programmatic workflows.
              </p>
            </div>
            <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
              {developerFeatures.map((feature) => (
                <div key={feature.title} className="flex gap-4">
                  <div className="h-10 w-10 rounded-lg bg-muted flex items-center justify-center flex-shrink-0">
                    <feature.icon className="h-5 w-5 text-muted-foreground" />
                  </div>
                  <div>
                    <h4 className="font-medium mb-1">{feature.title}</h4>
                    <p className="text-sm text-muted-foreground">{feature.description}</p>
                  </div>
                </div>
              ))}
            </div>
            <div className="text-center mt-8">
              <Link
                to="/docs"
                className="text-primary hover:underline inline-flex items-center gap-1"
              >
                View documentation <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ================================================================
          PRICING
          ================================================================ */}
      <section id="pricing" className="py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">Simple, Transparent Pricing</h2>
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
                      Best for Agencies
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
                    <Button className="w-full" variant={tier.highlighted ? "default" : "outline"}>
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
          FAQ - Agency objection handling
          ================================================================ */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 bg-muted/30">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">Frequently Asked Questions</h2>
          </div>

          <div className="space-y-4">
            {faqItems.map((faq, i) => (
              <div key={i} className="bg-card border rounded-xl overflow-hidden">
                <button
                  className="w-full p-6 text-left flex items-center justify-between"
                  onClick={() => setOpenFaq(openFaq === i ? null : i)}
                >
                  <span className="font-semibold pr-4">{faq.question}</span>
                  <ChevronDown
                    className={`h-5 w-5 text-muted-foreground transition-transform ${
                      openFaq === i ? "rotate-180" : ""
                    }`}
                  />
                </button>
                {openFaq === i && (
                  <div className="px-6 pb-6 text-muted-foreground">{faq.answer}</div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ================================================================
          FINAL CTA
          ================================================================ */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 bg-primary text-primary-foreground">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-bold mb-6">
            Ready to stop wasting generations?
          </h2>
          <p className="text-xl opacity-90 mb-8">
            Get ad-ready images faster with prompts that make the model stop guessing.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link to="/login">
              <Button size="lg" variant="secondary" className="text-lg px-8">
                Run a 7-day agency pilot
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <Link to="/login">
              <Button
                size="lg"
                variant="ghost"
                className="text-lg px-8 text-primary-foreground hover:text-primary-foreground hover:bg-primary-foreground/10"
              >
                Get Started Free
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
                <img src="/clarynt_icon.jpg" alt="Clayrnt" className="h-6 w-6" />
                <span className="text-lg font-bold">Clayrnt</span>
              </div>
              <p className="text-sm text-muted-foreground">
                Production-ready prompts for marketing agencies and creative studios.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>
                  <a href="#how-it-works" className="hover:text-foreground">
                    How it works
                  </a>
                </li>
                <li>
                  <a href="#features" className="hover:text-foreground">
                    Features
                  </a>
                </li>
                <li>
                  <a href="#pricing" className="hover:text-foreground">
                    Pricing
                  </a>
                </li>
                <li>
                  <Link to="/docs" className="hover:text-foreground">
                    Documentation
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Resources</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>
                  <Link to="/education" className="hover:text-foreground">
                    Best Practices
                  </Link>
                </li>
                <li>
                  <Link to="/docs#sdk" className="hover:text-foreground">
                    Python SDK
                  </Link>
                </li>
                <li>
                  <a href="#" className="hover:text-foreground">
                    API Reference
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>
                  <a href="#" className="hover:text-foreground">
                    About
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-foreground">
                    Contact
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-foreground">
                    Privacy Policy
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-foreground">
                    Terms of Service
                  </a>
                </li>
              </ul>
            </div>
          </div>
          <div className="border-t mt-12 pt-8 text-center text-sm text-muted-foreground">
            <p>&copy; {new Date().getFullYear()} Clayrnt. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
