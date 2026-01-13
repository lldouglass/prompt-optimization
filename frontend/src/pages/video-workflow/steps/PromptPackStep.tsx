import { useState, useEffect } from "react"
import { Loader2, FileText, Sparkles, Copy, Check } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { videoWorkflowApi, type VideoWorkflowDetail } from "@/lib/api"
import type { PromptPack, ShotPrompt } from "@/types/video-workflow"

interface PromptPackStepProps {
  workflow: VideoWorkflowDetail | null
  onComplete: () => void
  onRefresh: () => void
}

export function PromptPackStep({ workflow, onComplete, onRefresh }: PromptPackStepProps) {
  const [isGenerating, setIsGenerating] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [promptPack, setPromptPack] = useState<PromptPack | null>(null)
  const [activePrompt, setActivePrompt] = useState<number>(0)
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null)

  // Load existing prompt pack, or auto-generate if none exists
  useEffect(() => {
    if (workflow?.prompt_pack) {
      setPromptPack(workflow.prompt_pack)
    } else if (workflow?.shot_plan?.shots && !isGenerating && !promptPack) {
      // Auto-generate prompts if shots exist but no prompts yet
      handleGenerate()
    }
  }, [workflow])

  const handleGenerate = async () => {
    if (!workflow) return

    setIsGenerating(true)
    setError(null)

    try {
      const result = await videoWorkflowApi.generatePrompts(workflow.id, "sora_2")
      setPromptPack(result.prompt_pack)
      onRefresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate prompts")
    } finally {
      setIsGenerating(false)
    }
  }

  const handleSave = async () => {
    if (!workflow || !promptPack) return

    setIsSaving(true)
    setError(null)

    try {
      // Save each modified prompt
      for (let i = 0; i < promptPack.prompts.length; i++) {
        await videoWorkflowApi.updatePrompt(workflow.id, i, {
          prompt_text: promptPack.prompts[i].prompt_text,
          dialogue_block: promptPack.prompts[i].dialogue_block,
        })
      }
      onComplete()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save prompts")
    } finally {
      setIsSaving(false)
    }
  }

  const updatePrompt = (index: number, field: keyof ShotPrompt, value: string) => {
    if (!promptPack) return
    setPromptPack({
      ...promptPack,
      prompts: promptPack.prompts.map((p, i) =>
        i === index ? { ...p, [field]: value } : p
      ),
    })
  }

  const copyToClipboard = (text: string, index: number) => {
    navigator.clipboard.writeText(text)
    setCopiedIndex(index)
    setTimeout(() => setCopiedIndex(null), 2000)
  }

  const currentPrompt = promptPack?.prompts[activePrompt]

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          Prompt Pack - Sora 2
        </CardTitle>
        <CardDescription>
          Review and edit the compiled prompts for each shot.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Generate Button */}
        {!promptPack && (
          <div className="text-center py-8 space-y-4">
            <p className="text-muted-foreground">
              Generate Sora 2 prompts from your shot plan and continuity pack.
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
                  Generate Prompts
                </>
              )}
            </Button>
          </div>
        )}

        {/* Prompt Pack Editor */}
        {promptPack && (
          <>
            {/* Shot Tabs */}
            <div className="flex gap-2 overflow-x-auto pb-2">
              {promptPack.prompts.map((prompt, index) => (
                <Button
                  key={prompt.shot_id}
                  variant={activePrompt === index ? "default" : "outline"}
                  size="sm"
                  onClick={() => setActivePrompt(index)}
                >
                  Shot {index + 1}
                </Button>
              ))}
              <Button
                variant="outline"
                size="sm"
                onClick={handleGenerate}
                disabled={isGenerating}
              >
                {isGenerating ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Sparkles className="h-4 w-4" />
                )}
              </Button>
            </div>

            {/* Current Prompt Editor */}
            {currentPrompt && (
              <div className="space-y-4">
                {/* Parameters Badge */}
                <div className="flex gap-2 flex-wrap">
                  <Badge variant="secondary">
                    {currentPrompt.sora_params.duration}s
                  </Badge>
                  <Badge variant="secondary">
                    {currentPrompt.sora_params.aspect_ratio}
                  </Badge>
                  <Badge variant="secondary">
                    {currentPrompt.sora_params.resolution}
                  </Badge>
                  <Badge variant="secondary">
                    {currentPrompt.sora_params.fps} fps
                  </Badge>
                </div>

                {/* Main Prompt */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label>Prompt Text</Label>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => copyToClipboard(currentPrompt.prompt_text, activePrompt)}
                    >
                      {copiedIndex === activePrompt ? (
                        <Check className="h-4 w-4 text-green-600" />
                      ) : (
                        <Copy className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                  <Textarea
                    value={currentPrompt.prompt_text}
                    onChange={e => updatePrompt(activePrompt, "prompt_text", e.target.value)}
                    rows={10}
                    className="font-mono text-sm"
                  />
                  <p className="text-xs text-muted-foreground text-right">
                    {currentPrompt.prompt_text.length} characters
                  </p>
                </div>


                {/* Dialogue Block */}
                <div className="space-y-2">
                  <Label>Dialogue Block (Optional)</Label>
                  <Textarea
                    value={currentPrompt.dialogue_block || ""}
                    onChange={e => updatePrompt(activePrompt, "dialogue_block", e.target.value)}
                    rows={2}
                    placeholder="Dialogue or voiceover text for this shot..."
                  />
                </div>
              </div>
            )}
          </>
        )}

        {/* Error Display */}
        {error && (
          <div className="bg-destructive/10 text-destructive rounded-lg p-4">
            {error}
          </div>
        )}

        {/* Save Button */}
        {promptPack && (
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
