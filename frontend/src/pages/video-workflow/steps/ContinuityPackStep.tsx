import { useState, useEffect } from "react"
import { Loader2, Palette, Lightbulb, Sparkles, Plus, X } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { videoWorkflowApi, type VideoWorkflowDetail } from "@/lib/api"
import type { ContinuityPack, Anchor, LightingRecipe, PaletteAnchor } from "@/types/video-workflow"

interface ContinuityPackStepProps {
  workflow: VideoWorkflowDetail | null
  onComplete: () => void
  onRefresh: () => void
}

export function ContinuityPackStep({ workflow, onComplete, onRefresh }: ContinuityPackStepProps) {
  const [isGenerating, setIsGenerating] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [continuity, setContinuity] = useState<ContinuityPack | null>(null)

  // Load existing continuity pack, or auto-generate if none exists
  useEffect(() => {
    if (workflow?.continuity_pack) {
      setContinuity(workflow.continuity_pack)
    } else if (workflow?.brief && !isGenerating && !continuity) {
      // Only auto-generate if there are answered questions (meaning user went through Q&A)
      const hasAnsweredQuestions = workflow.brief.clarifying_questions?.some(
        (q: { answer?: string }) => q.answer && q.answer.trim().length > 0
      )
      if (hasAnsweredQuestions) {
        handleGenerate()
      }
    }
  }, [workflow])

  const handleGenerate = async () => {
    if (!workflow) return

    setIsGenerating(true)
    setError(null)

    try {
      const result = await videoWorkflowApi.generateContinuity(workflow.id)
      setContinuity(result.continuity_pack)
      onRefresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate continuity pack")
    } finally {
      setIsGenerating(false)
    }
  }

  const handleSave = async () => {
    if (!workflow || !continuity) return

    setIsSaving(true)
    setError(null)

    try {
      await videoWorkflowApi.updateContinuity(workflow.id, continuity)
      onComplete()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save continuity pack")
    } finally {
      setIsSaving(false)
    }
  }

  const updateAnchor = (index: number, field: keyof Anchor, value: string) => {
    if (!continuity) return
    setContinuity({
      ...continuity,
      anchors: continuity.anchors.map((a, i) =>
        i === index ? { ...a, [field]: value } : a
      ),
    })
  }

  const updateLighting = (field: keyof LightingRecipe, value: string) => {
    if (!continuity) return
    setContinuity({
      ...continuity,
      lighting_recipe: {
        ...(continuity.lighting_recipe || {
          key_light: "",
          fill_light: "",
          softness: "",
          time_of_day: "",
        }),
        [field]: value,
      },
    })
  }

  const updatePalette = (index: number, field: keyof PaletteAnchor, value: string) => {
    if (!continuity) return
    setContinuity({
      ...continuity,
      palette_anchors: continuity.palette_anchors.map((p, i) =>
        i === index ? { ...p, [field]: value } : p
      ),
    })
  }

  const updateList = (listName: "do_list" | "dont_list", index: number, value: string) => {
    if (!continuity) return
    setContinuity({
      ...continuity,
      [listName]: continuity[listName].map((item, i) => i === index ? value : item),
    })
  }

  const addToList = (listName: "do_list" | "dont_list") => {
    if (!continuity) return
    setContinuity({
      ...continuity,
      [listName]: [...continuity[listName], ""],
    })
  }

  const removeFromList = (listName: "do_list" | "dont_list", index: number) => {
    if (!continuity) return
    setContinuity({
      ...continuity,
      [listName]: continuity[listName].filter((_, i) => i !== index),
    })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Palette className="h-5 w-5" />
          Continuity Pack
        </CardTitle>
        <CardDescription>
          Define visual anchors, lighting, and style rules for consistent video generation.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Generate Button */}
        {!continuity && (
          <div className="text-center py-8 space-y-4">
            <p className="text-muted-foreground">
              Generate a continuity pack based on your brief and answers.
            </p>
            <Button onClick={handleGenerate} disabled={isGenerating}>
              {isGenerating ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4 mr-2" />
                  Generate Continuity Pack
                </>
              )}
            </Button>
          </div>
        )}

        {/* Continuity Pack Editor */}
        {continuity && (
          <>
            {/* Style Clause */}
            <div className="space-y-2">
              <Label>Style Clause</Label>
              <Textarea
                value={continuity.style_clause || ""}
                onChange={e => setContinuity({ ...continuity, style_clause: e.target.value })}
                placeholder="One sentence defining the overall visual style..."
                rows={2}
              />
            </div>

            {/* Visual Anchors */}
            <div className="space-y-3">
              <Label>Visual Anchors</Label>
              <p className="text-sm text-muted-foreground">
                Key visual elements that should remain consistent
              </p>
              {continuity.anchors.map((anchor, i) => (
                <div key={i} className="grid grid-cols-4 gap-2">
                  <Input
                    value={anchor.type}
                    onChange={e => updateAnchor(i, "type", e.target.value)}
                    placeholder="Type (character, product, etc.)"
                  />
                  <Input
                    className="col-span-3"
                    value={anchor.description}
                    onChange={e => updateAnchor(i, "description", e.target.value)}
                    placeholder="Description"
                  />
                </div>
              ))}
            </div>

            {/* Lighting Recipe */}
            <div className="space-y-3">
              <Label className="flex items-center gap-2">
                <Lightbulb className="h-4 w-4" />
                Lighting Recipe
              </Label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-xs">Key Light</Label>
                  <Input
                    value={continuity.lighting_recipe?.key_light || ""}
                    onChange={e => updateLighting("key_light", e.target.value)}
                    placeholder="Main light source"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-xs">Fill Light</Label>
                  <Input
                    value={continuity.lighting_recipe?.fill_light || ""}
                    onChange={e => updateLighting("fill_light", e.target.value)}
                    placeholder="Secondary light"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-xs">Softness</Label>
                  <Input
                    value={continuity.lighting_recipe?.softness || ""}
                    onChange={e => updateLighting("softness", e.target.value)}
                    placeholder="e.g., Very soft, no harsh shadows"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-xs">Time of Day</Label>
                  <Input
                    value={continuity.lighting_recipe?.time_of_day || ""}
                    onChange={e => updateLighting("time_of_day", e.target.value)}
                    placeholder="e.g., Golden hour, mid-morning"
                  />
                </div>
              </div>
            </div>

            {/* Color Palette */}
            <div className="space-y-3">
              <Label>Color Palette</Label>
              <div className="flex flex-wrap gap-3">
                {continuity.palette_anchors.map((color, i) => (
                  <div key={i} className="flex items-center gap-2 p-2 border rounded-lg">
                    <input
                      type="color"
                      value={color.hex}
                      onChange={e => updatePalette(i, "hex", e.target.value)}
                      className="w-8 h-8 rounded cursor-pointer"
                    />
                    <Input
                      value={color.name}
                      onChange={e => updatePalette(i, "name", e.target.value)}
                      placeholder="Color name"
                      className="w-28"
                    />
                  </div>
                ))}
              </div>
            </div>

            {/* Do List */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label className="text-green-600">Do List</Label>
                <Button variant="ghost" size="sm" onClick={() => addToList("do_list")}>
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
              {continuity.do_list.map((item, i) => (
                <div key={i} className="flex gap-2">
                  <Input
                    value={item}
                    onChange={e => updateList("do_list", i, e.target.value)}
                    placeholder="Guideline to follow..."
                  />
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => removeFromList("do_list", i)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>

            {/* Don't List */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label className="text-red-600">Don't List</Label>
                <Button variant="ghost" size="sm" onClick={() => addToList("dont_list")}>
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
              {continuity.dont_list.map((item, i) => (
                <div key={i} className="flex gap-2">
                  <Input
                    value={item}
                    onChange={e => updateList("dont_list", i, e.target.value)}
                    placeholder="Thing to avoid..."
                  />
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => removeFromList("dont_list", i)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>

            {/* Regenerate Button */}
            <Button
              variant="outline"
              onClick={handleGenerate}
              disabled={isGenerating}
            >
              {isGenerating ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Sparkles className="h-4 w-4 mr-2" />
              )}
              Regenerate
            </Button>
          </>
        )}

        {/* Error Display */}
        {error && (
          <div className="bg-destructive/10 text-destructive rounded-lg p-4">
            {error}
          </div>
        )}

        {/* Save Button */}
        {continuity && (
          <div className="flex justify-end">
            <Button onClick={handleSave} disabled={isSaving}>
              {isSaving ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                "Save & Continue"
              )}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
