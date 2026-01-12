import { Link } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { useSEO } from "@/hooks/useSEO"
import { Palette, Image, Video, Wand2, CheckCircle, ArrowRight, Layers, Eye, Sparkles } from "lucide-react"

export function CreativeStudiosPage() {
  useSEO({
    title: "Prompt Optimization for Creative Studios | Clarynt",
    description: "Clarynt empowers creative studios to master AI image and video generation. Optimize prompts for Midjourney, DALL-E, Runway, and more. Get consistent visual results with prompt blueprints and quality scoring.",
    canonical: "https://app.clarynt.net/creative-studios",
  })

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-gray-50 dark:from-gray-950 dark:to-gray-900">
      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="max-w-6xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-pink-100 dark:bg-pink-900/30 text-pink-700 dark:text-pink-300 px-4 py-2 rounded-full text-sm font-medium mb-8">
            <Palette className="h-4 w-4" />
            Built for Visual Creators
          </div>

          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6">
            Prompt Optimization for Creative Studios
          </h1>

          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto mb-10">
            Turn your creative vision into precise AI prompts. Clarynt helps creative studios get
            consistent, high-quality visual outputs from Midjourney, DALL-E, Runway, and more.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/login">
              <Button size="lg" className="w-full sm:w-auto">
                Start Creating Free <ArrowRight className="ml-2 h-4 w-4" />
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

      {/* The Creative Challenge */}
      <section className="py-16 px-4 bg-white dark:bg-gray-900">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4 text-gray-900 dark:text-white">
            The Creative Studio AI Challenge
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-300 text-center max-w-3xl mx-auto mb-12">
            AI image and video tools are powerful, but translating creative intent into prompts is an art form.
          </p>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-gray-50 dark:bg-gray-800 rounded-xl p-6">
              <div className="w-12 h-12 bg-red-100 dark:bg-red-900/30 rounded-xl flex items-center justify-center mb-4">
                <Eye className="h-6 w-6 text-red-600 dark:text-red-400" />
              </div>
              <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">Vision Lost in Translation</h3>
              <p className="text-gray-600 dark:text-gray-400">
                The image in your head rarely matches the AI output. Prompts don't capture the nuance of your creative direction.
              </p>
            </div>

            <div className="bg-gray-50 dark:bg-gray-800 rounded-xl p-6">
              <div className="w-12 h-12 bg-red-100 dark:bg-red-900/30 rounded-xl flex items-center justify-center mb-4">
                <Layers className="h-6 w-6 text-red-600 dark:text-red-400" />
              </div>
              <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">Style Inconsistency</h3>
              <p className="text-gray-600 dark:text-gray-400">
                Getting consistent style across a series of images or video clips feels impossible without precise prompts.
              </p>
            </div>

            <div className="bg-gray-50 dark:bg-gray-800 rounded-xl p-6">
              <div className="w-12 h-12 bg-red-100 dark:bg-red-900/30 rounded-xl flex items-center justify-center mb-4">
                <Wand2 className="h-6 w-6 text-red-600 dark:text-red-400" />
              </div>
              <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">Model-Specific Syntax</h3>
              <p className="text-gray-600 dark:text-gray-400">
                Each AI tool has different prompt conventions. What works in Midjourney fails in DALL-E.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Solution */}
      <section className="py-16 px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4 text-gray-900 dark:text-white">
            How Clarynt Helps Creative Studios
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-300 text-center max-w-2xl mx-auto mb-12">
            Bridge the gap between creative vision and AI output with intelligent prompt optimization.
          </p>

          <div className="grid md:grid-cols-2 gap-8">
            <div className="flex gap-4">
              <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-xl flex items-center justify-center flex-shrink-0">
                <Image className="h-6 w-6 text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">Image Prompt Optimization</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Optimize prompts for Midjourney, DALL-E, Stable Diffusion, and other image generators. Get precise control over style, composition, and mood.
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-xl flex items-center justify-center flex-shrink-0">
                <Video className="h-6 w-6 text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">Video Prompt Engineering</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Craft prompts for Runway, Pika, and other video AI tools. Define camera movements, transitions, and timing with precision.
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-xl flex items-center justify-center flex-shrink-0">
                <Sparkles className="h-6 w-6 text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">Clarifying Questions</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Our AI asks the right questions about lighting, perspective, style references, and more to capture your full creative intent.
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-xl flex items-center justify-center flex-shrink-0">
                <Layers className="h-6 w-6 text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">Style Consistency</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Save and reuse prompt templates to maintain visual consistency across projects and team members.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Supported Tools */}
      <section className="py-16 px-4 bg-white dark:bg-gray-900">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4 text-gray-900 dark:text-white">
            Optimize Prompts for Any AI Tool
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-300 text-center max-w-2xl mx-auto mb-12">
            Clarynt understands the syntax and best practices for all major creative AI platforms.
          </p>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { name: "Midjourney", type: "Image Generation" },
              { name: "DALL-E 3", type: "Image Generation" },
              { name: "Stable Diffusion", type: "Image Generation" },
              { name: "Runway Gen-3", type: "Video Generation" },
              { name: "Pika Labs", type: "Video Generation" },
              { name: "Leonardo AI", type: "Image Generation" },
              { name: "Ideogram", type: "Image Generation" },
              { name: "Sora", type: "Video Generation" },
            ].map((tool) => (
              <div key={tool.name} className="bg-gray-50 dark:bg-gray-800 rounded-xl p-4 text-center">
                <h3 className="font-semibold text-gray-900 dark:text-white">{tool.name}</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">{tool.type}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section className="py-16 px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-900 dark:text-white">
            Creative Studio Use Cases
          </h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              "Brand visual development",
              "Social media graphics",
              "Marketing campaign assets",
              "Product visualization",
              "Concept art exploration",
              "Video content creation",
              "Storyboard visualization",
              "Character design iterations",
              "Motion graphics elements",
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
      <section className="py-20 px-4 bg-gradient-to-r from-purple-600 to-pink-600">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4 text-white">
            Ready to Elevate Your Visual AI Workflow?
          </h2>
          <p className="text-lg text-purple-100 mb-8">
            Join creative studios who are getting predictable, high-quality AI visuals with Clarynt.
          </p>
          <Link to="/login">
            <Button size="lg" variant="secondary">
              Start Free Today <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-gray-200 dark:border-gray-800">
        <div className="max-w-6xl mx-auto flex flex-wrap justify-center gap-6 text-sm text-gray-600 dark:text-gray-400">
          <Link to="/" className="hover:text-purple-600">Home</Link>
          <Link to="/prompt-optimization" className="hover:text-purple-600">Prompt Optimization</Link>
          <Link to="/marketing-agencies" className="hover:text-purple-600">For Marketing Agencies</Link>
          <Link to="/docs" className="hover:text-purple-600">Documentation</Link>
          <Link to="/education" className="hover:text-purple-600">Education</Link>
        </div>
      </footer>
    </div>
  )
}
