import { useState, useEffect } from "react"
import { Loader2 } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { videoWorkflowApi, type VideoWorkflowDetail } from "@/lib/api"
import {
  type BriefIntake,
  GOAL_OPTIONS,
  PLATFORM_OPTIONS,
  ASPECT_RATIO_OPTIONS,
  DURATION_OPTIONS,
} from "@/types/video-workflow"

interface BriefIntakeStepProps {
  workflow: VideoWorkflowDetail | null
  onComplete: () => void
}

export function BriefIntakeStep({ workflow, onComplete }: BriefIntakeStepProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Form state
  const [formData, setFormData] = useState<BriefIntake>({
    project_name: "",
    goal: "product_ad",
    platform: "instagram",
    aspect_ratio: "9:16",
    duration_seconds: 15,
    brand_vibe: ["", "", ""],
    avoid_vibe: ["", "", ""],
    must_include: [],
    must_avoid: [],
    script_or_vo: "",
    product_or_subject_description: "",
    reference_images: [],
  })

  // Must include/avoid as comma-separated strings for easier editing
  const [mustIncludeText, setMustIncludeText] = useState("")
  const [mustAvoidText, setMustAvoidText] = useState("")

  // Load existing brief data
  useEffect(() => {
    if (workflow?.brief) {
      const brief = workflow.brief
      setFormData({
        project_name: brief.project_name || "",
        goal: brief.goal || "product_ad",
        platform: brief.platform || "instagram",
        aspect_ratio: brief.aspect_ratio || "9:16",
        duration_seconds: brief.duration_seconds || 15,
        brand_vibe: brief.brand_vibe || ["", "", ""],
        avoid_vibe: brief.avoid_vibe || ["", "", ""],
        must_include: brief.must_include || [],
        must_avoid: brief.must_avoid || [],
        script_or_vo: brief.script_or_vo || "",
        product_or_subject_description: brief.product_or_subject_description || "",
        reference_images: brief.reference_images || [],
      })
      setMustIncludeText((brief.must_include || []).join(", "))
      setMustAvoidText((brief.must_avoid || []).join(", "))
    }
  }, [workflow])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!workflow) {
      setError("Workflow not created yet")
      return
    }

    setIsSubmitting(true)
    setError(null)

    try {
      // Convert comma-separated text to arrays
      const briefData: BriefIntake = {
        ...formData,
        brand_vibe: formData.brand_vibe.filter(v => v.trim()),
        avoid_vibe: formData.avoid_vibe.filter(v => v.trim()),
        must_include: mustIncludeText.split(",").map(s => s.trim()).filter(Boolean),
        must_avoid: mustAvoidText.split(",").map(s => s.trim()).filter(Boolean),
      }

      await videoWorkflowApi.saveBrief(workflow.id, briefData)
      onComplete()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save brief")
    } finally {
      setIsSubmitting(false)
    }
  }

  const updateVibeWord = (type: "brand_vibe" | "avoid_vibe", index: number, value: string) => {
    setFormData(prev => ({
      ...prev,
      [type]: prev[type].map((v, i) => i === index ? value : v),
    }))
  }

  return (
    <form onSubmit={handleSubmit}>
      <Card>
        <CardHeader>
          <CardTitle>Brief Intake</CardTitle>
          <CardDescription>
            Tell us about your video project. The more detail you provide, the better your prompts will be.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Project Name */}
          <div className="space-y-2">
            <Label htmlFor="project_name">Project Name *</Label>
            <Input
              id="project_name"
              value={formData.project_name}
              onChange={e => setFormData(prev => ({ ...prev, project_name: e.target.value }))}
              placeholder="e.g., Summer Collection Launch"
              required
            />
          </div>

          {/* Goal & Platform */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Goal *</Label>
              <div className="flex flex-wrap gap-2">
                {GOAL_OPTIONS.map(option => (
                  <Button
                    key={option.value}
                    type="button"
                    variant={formData.goal === option.value ? "default" : "outline"}
                    size="sm"
                    onClick={() => setFormData(prev => ({ ...prev, goal: option.value }))}
                  >
                    {option.label}
                  </Button>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <Label>Platform *</Label>
              <div className="flex flex-wrap gap-2">
                {PLATFORM_OPTIONS.map(option => (
                  <Button
                    key={option.value}
                    type="button"
                    variant={formData.platform === option.value ? "default" : "outline"}
                    size="sm"
                    onClick={() => setFormData(prev => ({ ...prev, platform: option.value }))}
                  >
                    {option.label}
                  </Button>
                ))}
              </div>
            </div>
          </div>

          {/* Aspect Ratio & Duration */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Aspect Ratio *</Label>
              <div className="flex flex-wrap gap-2">
                {ASPECT_RATIO_OPTIONS.map(option => (
                  <Button
                    key={option.value}
                    type="button"
                    variant={formData.aspect_ratio === option.value ? "default" : "outline"}
                    size="sm"
                    onClick={() => setFormData(prev => ({ ...prev, aspect_ratio: option.value }))}
                  >
                    {option.label}
                  </Button>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <Label>Duration (seconds) *</Label>
              <div className="flex flex-wrap gap-2">
                {DURATION_OPTIONS.map(duration => (
                  <Button
                    key={duration}
                    type="button"
                    variant={formData.duration_seconds === duration ? "default" : "outline"}
                    size="sm"
                    onClick={() => setFormData(prev => ({ ...prev, duration_seconds: duration }))}
                  >
                    {duration}s
                  </Button>
                ))}
              </div>
            </div>
          </div>

          {/* Brand Vibe */}
          <div className="space-y-2">
            <Label>Brand Vibe (3 words) *</Label>
            <p className="text-sm text-muted-foreground">
              Describe the feeling you want to evoke
            </p>
            <div className="grid grid-cols-3 gap-2">
              {[0, 1, 2].map(i => (
                <Input
                  key={i}
                  value={formData.brand_vibe[i] || ""}
                  onChange={e => updateVibeWord("brand_vibe", i, e.target.value)}
                  placeholder={["e.g., warm", "artisan", "cozy"][i]}
                  maxLength={30}
                />
              ))}
            </div>
          </div>

          {/* Avoid Vibe */}
          <div className="space-y-2">
            <Label>Avoid Vibe (3 words)</Label>
            <p className="text-sm text-muted-foreground">
              What feeling do you want to stay away from?
            </p>
            <div className="grid grid-cols-3 gap-2">
              {[0, 1, 2].map(i => (
                <Input
                  key={i}
                  value={formData.avoid_vibe[i] || ""}
                  onChange={e => updateVibeWord("avoid_vibe", i, e.target.value)}
                  placeholder={["e.g., corporate", "cold", "rushed"][i]}
                  maxLength={30}
                />
              ))}
            </div>
          </div>

          {/* Subject Description */}
          <div className="space-y-2">
            <Label htmlFor="subject">Product or Subject Description *</Label>
            <Textarea
              id="subject"
              value={formData.product_or_subject_description}
              onChange={e => setFormData(prev => ({ ...prev, product_or_subject_description: e.target.value }))}
              placeholder="Describe what/who should be featured in the video. Be specific about appearance, setting, and any key details."
              rows={4}
              required
            />
          </div>

          {/* Must Include / Must Avoid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="must_include">Must Include</Label>
              <p className="text-sm text-muted-foreground">Comma-separated list</p>
              <Input
                id="must_include"
                value={mustIncludeText}
                onChange={e => setMustIncludeText(e.target.value)}
                placeholder="e.g., logo, product close-up, tagline"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="must_avoid">Must Avoid</Label>
              <p className="text-sm text-muted-foreground">Comma-separated list</p>
              <Input
                id="must_avoid"
                value={mustAvoidText}
                onChange={e => setMustAvoidText(e.target.value)}
                placeholder="e.g., competitor colors, certain gestures"
              />
            </div>
          </div>

          {/* Script/VO */}
          <div className="space-y-2">
            <Label htmlFor="script">Script or Voiceover (optional)</Label>
            <Textarea
              id="script"
              value={formData.script_or_vo || ""}
              onChange={e => setFormData(prev => ({ ...prev, script_or_vo: e.target.value }))}
              placeholder="If you have a script or voiceover text, paste it here..."
              rows={3}
            />
          </div>

          {/* Error Display */}
          {error && (
            <div className="bg-destructive/10 text-destructive rounded-lg p-4">
              {error}
            </div>
          )}

          {/* Submit Button */}
          <div className="flex justify-end">
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                "Save & Continue"
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </form>
  )
}
