import { Link } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { useSEO } from "@/hooks/useSEO"
import { Building2, Users, Target, Clock, CheckCircle, ArrowRight, Repeat, Shield, TrendingUp } from "lucide-react"

export function MarketingAgenciesPage() {
  useSEO({
    title: "Prompt Optimization for Marketing Agencies | Clarynt",
    description: "Clarynt helps marketing agencies scale AI content creation. Deliver consistent, brand-aligned AI outputs across clients with prompt optimization, quality scoring, and team-wide prompt libraries.",
    canonical: "https://app.clarynt.net/marketing-agencies",
  })

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-gray-50 dark:from-gray-950 dark:to-gray-900">
      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="max-w-6xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 px-4 py-2 rounded-full text-sm font-medium mb-8">
            <Building2 className="h-4 w-4" />
            Built for Marketing Teams
          </div>

          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6">
            Prompt Optimization for Marketing Agencies
          </h1>

          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto mb-10">
            Scale AI content creation across clients without sacrificing quality. Clarynt helps your team
            deliver consistent, brand-aligned AI outputs every time.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/login">
              <Button size="lg" className="w-full sm:w-auto">
                Start Free Trial <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
            <Link to="/prompt-optimization">
              <Button variant="outline" size="lg" className="w-full sm:w-auto">
                Learn About Prompt Optimization
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Pain Points */}
      <section className="py-16 px-4 bg-white dark:bg-gray-900">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4 text-gray-900 dark:text-white">
            The Marketing Agency AI Challenge
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-300 text-center max-w-3xl mx-auto mb-12">
            AI tools promise efficiency, but without proper prompt engineering, agencies face real problems.
          </p>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-gray-50 dark:bg-gray-800 rounded-xl p-6">
              <div className="w-12 h-12 bg-red-100 dark:bg-red-900/30 rounded-xl flex items-center justify-center mb-4">
                <Users className="h-6 w-6 text-red-600 dark:text-red-400" />
              </div>
              <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">Inconsistent Team Output</h3>
              <p className="text-gray-600 dark:text-gray-400">
                Every team member prompts differently, leading to wildly varying quality and style across projects.
              </p>
            </div>

            <div className="bg-gray-50 dark:bg-gray-800 rounded-xl p-6">
              <div className="w-12 h-12 bg-red-100 dark:bg-red-900/30 rounded-xl flex items-center justify-center mb-4">
                <Clock className="h-6 w-6 text-red-600 dark:text-red-400" />
              </div>
              <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">Time Wasted on Revisions</h3>
              <p className="text-gray-600 dark:text-gray-400">
                Vague prompts lead to poor AI outputs, requiring multiple rounds of regeneration and manual editing.
              </p>
            </div>

            <div className="bg-gray-50 dark:bg-gray-800 rounded-xl p-6">
              <div className="w-12 h-12 bg-red-100 dark:bg-red-900/30 rounded-xl flex items-center justify-center mb-4">
                <Target className="h-6 w-6 text-red-600 dark:text-red-400" />
              </div>
              <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">Off-Brand Results</h3>
              <p className="text-gray-600 dark:text-gray-400">
                Generic prompts produce generic content that doesn't match client brand guidelines or voice.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Solution */}
      <section className="py-16 px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4 text-gray-900 dark:text-white">
            How Clarynt Helps Marketing Agencies
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-300 text-center max-w-2xl mx-auto mb-12">
            Turn AI tools into reliable, scalable content engines for your agency.
          </p>

          <div className="grid md:grid-cols-2 gap-8">
            <div className="flex gap-4">
              <div className="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-xl flex items-center justify-center flex-shrink-0">
                <Repeat className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">Repeatable Prompt Templates</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Build a library of optimized prompts for common tasks: social posts, ad copy, email campaigns. New team members get up to speed instantly.
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-xl flex items-center justify-center flex-shrink-0">
                <Shield className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">Brand Consistency</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Bake brand guidelines into your prompts. Clarynt's clarifying questions ensure every output aligns with client expectations.
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-xl flex items-center justify-center flex-shrink-0">
                <TrendingUp className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">Quality Before Generation</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  See prompt quality scores before you run them. Catch issues early and reduce revision cycles.
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-xl flex items-center justify-center flex-shrink-0">
                <Users className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">Team-Wide Access</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Share optimized prompts across your agency. Everyone uses the same high-quality templates.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section className="py-16 px-4 bg-white dark:bg-gray-900">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-900 dark:text-white">
            Marketing Agency Use Cases
          </h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              "Social media content calendars",
              "Ad copy variations for A/B testing",
              "Email marketing campaigns",
              "Blog post outlines and drafts",
              "Product descriptions at scale",
              "Client presentation content",
              "Video script generation",
              "Landing page copy",
              "Press release drafts",
            ].map((useCase) => (
              <div key={useCase} className="flex items-center gap-3 bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0" />
                <span className="text-gray-700 dark:text-gray-300">{useCase}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4 text-gray-900 dark:text-white">
            Ready to Scale Your Agency's AI Workflow?
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-300 mb-8">
            Join marketing agencies who are delivering consistent, high-quality AI content with Clarynt.
          </p>
          <Link to="/login">
            <Button size="lg">
              Get Started Free <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-gray-200 dark:border-gray-800">
        <div className="max-w-6xl mx-auto flex flex-wrap justify-center gap-6 text-sm text-gray-600 dark:text-gray-400">
          <Link to="/" className="hover:text-purple-600">Home</Link>
          <Link to="/prompt-optimization" className="hover:text-purple-600">Prompt Optimization</Link>
          <Link to="/creative-studios" className="hover:text-purple-600">For Creative Studios</Link>
          <Link to="/docs" className="hover:text-purple-600">Documentation</Link>
          <Link to="/education" className="hover:text-purple-600">Education</Link>
        </div>
      </footer>
    </div>
  )
}
