import { useState, useEffect } from "react"
import { Loader2, Film, Sparkles, ChevronDown, ChevronUp } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { videoWorkflowApi, type VideoWorkflowDetail } from "@/lib/api"
import type { Shot, ShotPlan } from "@/types/video-workflow"
import { SHOT_TYPE_OPTIONS, CAMERA_MOVE_OPTIONS } from "@/types/video-workflow"

interface ShotPlanStepProps {
  workflow: VideoWorkflowDetail | null
  onComplete: () => void
  onRefresh: () => void
}

export function ShotPlanStep({ workflow, onComplete, onRefresh }: ShotPlanStepProps) {
  const [isGenerating, setIsGenerating] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [shotPlan, setShotPlan] = useState<ShotPlan | null>(null)
  const [expandedShot, setExpandedShot] = useState<number | null>(null)

  // Load existing shot plan
  useEffect(() => {
    if (workflow?.shot_plan) {
      setShotPlan(workflow.shot_plan)
    }
  }, [workflow])

  const handleGenerate = async () => {
    if (!workflow) return

    setIsGenerating(true)
    setError(null)

    try {
      const result = await videoWorkflowApi.generateShots(workflow.id)
      setShotPlan(result.shot_plan)
      onRefresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate shot plan")
    } finally {
      setIsGenerating(false)
    }
  }

  const handleSave = async () => {
    if (!workflow || !shotPlan) return

    setIsSaving(true)
    setError(null)

    try {
      // Save each modified shot
      for (let i = 0; i < shotPlan.shots.length; i++) {
        await videoWorkflowApi.updateShot(workflow.id, i, shotPlan.shots[i])
      }
      onComplete()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save shot plan")
    } finally {
      setIsSaving(false)
    }
  }

  const updateShot = (index: number, field: keyof Shot, value: unknown) => {
    if (!shotPlan) return
    setShotPlan({
      ...shotPlan,
      shots: shotPlan.shots.map((s, i) =>
        i === index ? { ...s, [field]: value } : s
      ),
    })
  }

  const toggleExpand = (index: number) => {
    setExpandedShot(expandedShot === index ? null : index)
  }

  const totalDuration = shotPlan?.shots.reduce((sum, s) => sum + (s.end_sec - s.start_sec), 0) || 0

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Film className="h-5 w-5" />
          Shot Plan
        </CardTitle>
        <CardDescription>
          Plan your shots with timing, camera moves, and action beats.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Generate Button */}
        {!shotPlan && (
          <div className="text-center py-8 space-y-4">
            <p className="text-muted-foreground">
              Generate a shot plan based on your brief and continuity pack.
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
                  Generate Shot Plan
                </>
              )}
            </Button>
          </div>
        )}

        {/* Shot Plan Editor */}
        {shotPlan && (
          <>
            {/* Timeline Summary */}
            <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
              <div>
                <span className="font-medium">{shotPlan.shots.length} Shots</span>
                <span className="text-muted-foreground ml-2">
                  Total: {totalDuration.toFixed(1)}s
                </span>
              </div>
              <Button
                variant="outline"
                onClick={handleGenerate}
                disabled={isGenerating}
                size="sm"
              >
                {isGenerating ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Sparkles className="h-4 w-4 mr-2" />
                )}
                Regenerate
              </Button>
            </div>

            {/* Shot Cards */}
            <div className="space-y-4">
              {shotPlan.shots.map((shot, index) => (
                <div
                  key={shot.id}
                  className="border rounded-lg overflow-hidden"
                >
                  {/* Shot Header */}
                  <button
                    className="w-full flex items-center justify-between p-4 hover:bg-muted/50 transition-colors"
                    onClick={() => toggleExpand(index)}
                  >
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-lg">#{shot.shot_number}</span>
                        <Badge variant="outline">{shot.shot_type}</Badge>
                        <Badge variant="secondary">{shot.camera_move}</Badge>
                      </div>
                      <span className="text-sm text-muted-foreground">
                        {shot.start_sec.toFixed(1)}s - {shot.end_sec.toFixed(1)}s
                        ({(shot.end_sec - shot.start_sec).toFixed(1)}s)
                      </span>
                    </div>
                    {expandedShot === index ? (
                      <ChevronUp className="h-5 w-5" />
                    ) : (
                      <ChevronDown className="h-5 w-5" />
                    )}
                  </button>

                  {/* Shot Details (expanded) */}
                  {expandedShot === index && (
                    <div className="p-4 pt-0 space-y-4 border-t">
                      {/* Timing */}
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label>Start (sec)</Label>
                          <Input
                            type="number"
                            step="0.1"
                            value={shot.start_sec}
                            onChange={e => updateShot(index, "start_sec", parseFloat(e.target.value))}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>End (sec)</Label>
                          <Input
                            type="number"
                            step="0.1"
                            value={shot.end_sec}
                            onChange={e => updateShot(index, "end_sec", parseFloat(e.target.value))}
                          />
                        </div>
                      </div>

                      {/* Shot Type & Camera */}
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label>Shot Type</Label>
                          <div className="flex flex-wrap gap-2">
                            {SHOT_TYPE_OPTIONS.map(opt => (
                              <Button
                                key={opt.value}
                                type="button"
                                variant={shot.shot_type === opt.value ? "default" : "outline"}
                                size="sm"
                                onClick={() => updateShot(index, "shot_type", opt.value)}
                              >
                                {opt.label}
                              </Button>
                            ))}
                          </div>
                        </div>
                        <div className="space-y-2">
                          <Label>Camera Move</Label>
                          <div className="flex flex-wrap gap-2">
                            {CAMERA_MOVE_OPTIONS.map(opt => (
                              <Button
                                key={opt.value}
                                type="button"
                                variant={shot.camera_move === opt.value ? "default" : "outline"}
                                size="sm"
                                onClick={() => updateShot(index, "camera_move", opt.value)}
                              >
                                {opt.label}
                              </Button>
                            ))}
                          </div>
                        </div>
                      </div>

                      {/* Framing Notes */}
                      <div className="space-y-2">
                        <Label>Framing Notes</Label>
                        <Textarea
                          value={shot.framing_notes}
                          onChange={e => updateShot(index, "framing_notes", e.target.value)}
                          rows={2}
                        />
                      </div>

                      {/* Action Beats */}
                      <div className="space-y-2">
                        <Label>Action Beats</Label>
                        <div className="space-y-2">
                          {shot.subject_action_beats.map((beat, beatIndex) => (
                            <Input
                              key={beatIndex}
                              value={beat}
                              onChange={e => {
                                const newBeats = [...shot.subject_action_beats]
                                newBeats[beatIndex] = e.target.value
                                updateShot(index, "subject_action_beats", newBeats)
                              }}
                              placeholder={`Beat ${beatIndex + 1}`}
                            />
                          ))}
                        </div>
                      </div>

                      {/* Purpose */}
                      <div className="space-y-2">
                        <Label>Purpose</Label>
                        <Input
                          value={shot.purpose}
                          onChange={e => updateShot(index, "purpose", e.target.value)}
                          placeholder="What this shot communicates..."
                        />
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </>
        )}

        {/* Error Display */}
        {error && (
          <div className="bg-destructive/10 text-destructive rounded-lg p-4">
            {error}
          </div>
        )}

        {/* Save Button */}
        {shotPlan && (
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
