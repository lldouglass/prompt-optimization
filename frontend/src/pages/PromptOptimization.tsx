import { Link } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { useSEO } from "@/hooks/useSEO"
import { Sparkles, Target, Zap, CheckCircle, ArrowRight, BarChart3, MessageSquare, FileText } from "lucide-react"

export function PromptOptimizationPage() {
  useSEO({
    title: "Prompt Optimization - Turn Vague Ideas into High-Fidelity AI Prompts | Clarynt",
    description: "Master prompt optimization with Clarynt. Our AI-powered engine transforms rough ideas into precise, repeatable prompts. Features clarifying questions, quality scoring, and prompt blueprints for ChatGPT, Midjourney, and more.",
    canonical: "https://app.clarynt.net/prompt-optimization",
  })

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-gray-50 dark:from-gray-950 dark:to-gray-900">
      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="max-w-6xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 px-4 py-2 rounded-full text-sm font-medium mb-8">
            <Sparkles className="h-4 w-4" />
            AI-Powered Prompt Engineering
          </div>

          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6">
            Prompt Optimization That Actually Works
          </h1>

          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto mb-10">
            Stop guessing. Start optimizing. Clarynt transforms your rough creative ideas into
            precise, repeatable prompts that deliver consistent results every time.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/login">
              <Button size="lg" className="w-full sm:w-auto">
                Start Optimizing Free <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
            <Link to="/docs">
              <Button variant="outline" size="lg" className="w-full sm:w-auto">
                View Documentation
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* What is Prompt Optimization */}
      <section className="py-16 px-4 bg-white dark:bg-gray-900">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4 text-gray-900 dark:text-white">
            What is Prompt Optimization?
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-300 text-center max-w-3xl mx-auto mb-12">
            Prompt optimization is the process of refining AI prompts to get better, more consistent results.
            It's the difference between "make me a logo" and getting exactly the brand asset you envisioned.
          </p>

          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-red-50 dark:bg-red-900/20 rounded-xl p-6 border border-red-200 dark:border-red-800">
              <h3 className="text-lg font-semibold text-red-700 dark:text-red-400 mb-3">
                Without Prompt Optimization
              </h3>
              <ul className="space-y-2 text-gray-700 dark:text-gray-300">
                <li className="flex items-start gap-2">
                  <span className="text-red-500 mt-1">✗</span>
                  Vague prompts lead to unpredictable outputs
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-500 mt-1">✗</span>
                  Hours wasted on trial and error
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-500 mt-1">✗</span>
                  Inconsistent results across team members
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-500 mt-1">✗</span>
                  No way to measure prompt quality
                </li>
              </ul>
            </div>

            <div className="bg-green-50 dark:bg-green-900/20 rounded-xl p-6 border border-green-200 dark:border-green-800">
              <h3 className="text-lg font-semibold text-green-700 dark:text-green-400 mb-3">
                With Clarynt Prompt Optimization
              </h3>
              <ul className="space-y-2 text-gray-700 dark:text-gray-300">
                <li className="flex items-start gap-2">
                  <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  Precise prompts with clear intent
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  Get quality results on the first try
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  Shareable prompt library for teams
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  Quality scoring before you run
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-16 px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4 text-gray-900 dark:text-white">
            How Prompt Optimization Works
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-300 text-center max-w-2xl mx-auto mb-12">
            Our AI-powered engine analyzes your prompts and provides actionable improvements.
          </p>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 dark:bg-purple-900/30 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <MessageSquare className="h-8 w-8 text-purple-600 dark:text-purple-400" />
              </div>
              <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">1. Input Your Prompt</h3>
              <p className="text-gray-600 dark:text-gray-400">
                Paste your existing prompt or describe what you're trying to achieve. Works with ChatGPT, Midjourney, DALL-E, and more.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 dark:bg-purple-900/30 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Target className="h-8 w-8 text-purple-600 dark:text-purple-400" />
              </div>
              <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">2. AI Analysis</h3>
              <p className="text-gray-600 dark:text-gray-400">
                Our engine identifies ambiguities, missing context, and areas for improvement. You'll see exactly what's working and what isn't.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 dark:bg-purple-900/30 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Zap className="h-8 w-8 text-purple-600 dark:text-purple-400" />
              </div>
              <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">3. Get Optimized Prompt</h3>
              <p className="text-gray-600 dark:text-gray-400">
                Receive an enhanced prompt with quality scoring. Save it to your library for future use and team sharing.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 px-4 bg-white dark:bg-gray-900">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-900 dark:text-white">
            Prompt Optimization Features
          </h2>

          <div className="grid md:grid-cols-2 gap-8">
            <div className="flex gap-4">
              <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-xl flex items-center justify-center flex-shrink-0">
                <MessageSquare className="h-6 w-6 text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">Clarifying Questions</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Our AI asks targeted questions to understand your intent, filling in gaps that would otherwise lead to poor results.
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-xl flex items-center justify-center flex-shrink-0">
                <BarChart3 className="h-6 w-6 text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">Quality Scoring</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  See objective scores for clarity, specificity, and effectiveness before you run your prompt.
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-xl flex items-center justify-center flex-shrink-0">
                <FileText className="h-6 w-6 text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">Prompt Library</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Save, organize, and reuse your best prompts. Build a library of proven templates for your team.
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-xl flex items-center justify-center flex-shrink-0">
                <Sparkles className="h-6 w-6 text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">Web-Grounded Examples</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Our engine searches for real-world examples and documentation to inform better prompt suggestions.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4 text-gray-900 dark:text-white">
            Ready to Optimize Your Prompts?
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-300 mb-8">
            Join marketing agencies and creative studios who are getting better AI results with Clarynt.
          </p>
          <Link to="/login">
            <Button size="lg">
              Start Free Today <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-gray-200 dark:border-gray-800">
        <div className="max-w-6xl mx-auto flex flex-wrap justify-center gap-6 text-sm text-gray-600 dark:text-gray-400">
          <Link to="/" className="hover:text-purple-600">Home</Link>
          <Link to="/marketing-agencies" className="hover:text-purple-600">For Marketing Agencies</Link>
          <Link to="/creative-studios" className="hover:text-purple-600">For Creative Studios</Link>
          <Link to="/docs" className="hover:text-purple-600">Documentation</Link>
          <Link to="/education" className="hover:text-purple-600">Education</Link>
        </div>
      </footer>
    </div>
  )
}
