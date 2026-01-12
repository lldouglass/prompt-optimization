import { useState, useEffect } from "react"
import { Link, useParams } from "react-router-dom"
import {
  videoApi,
  type VideoPromptDetail,
  type VideoPromptVersion,
  type VideoPromptOutput,
} from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import {
  ArrowLeft,
  Save,
  Sparkles,
  Link as LinkIcon,
  ThumbsUp,
  ThumbsDown,
  Share2,
  Loader2,
  Copy,
  Check,
  Trash2,
  RotateCcw,
  Star,
  ExternalLink,
  X,
} from "lucide-react"

export function VideoPromptDetailPage() {
  const { promptId } = useParams<{ promptId: string }>()
  const [data, setData] = useState<VideoPromptDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<"editor" | "versions" | "outputs">("editor")

  // Editor state
  const [sceneDescription, setSceneDescription] = useState("")
  const [motionTiming, setMotionTiming] = useState("")
  const [styleTone, setStyleTone] = useState("")
  const [cameraLanguage, setCameraLanguage] = useState("")
  const [constraints, setConstraints] = useState("")
  const [negativeInstructions, setNegativeInstructions] = useState("")
  const [saving, setSaving] = useState(false)
  const [hasChanges, setHasChanges] = useState(false)

  // Variant generation
  const [generatingVariants, setGeneratingVariants] = useState(false)

  // Output attachment
  const [showAttachForm, setShowAttachForm] = useState(false)
  const [attachUrl, setAttachUrl] = useState("")
  const [attachNotes, setAttachNotes] = useState("")
  const [attaching, setAttaching] = useState(false)
  const [selectedVersionForOutput, setSelectedVersionForOutput] = useState<string | null>(null)

  // Share modal
  const [showShareModal, setShowShareModal] = useState(false)
  const [shareToken, setShareToken] = useState<string | null>(null)
  const [creatingShare, setCreatingShare] = useState(false)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    if (promptId) {
      loadPrompt()
    }
  }, [promptId])

  async function loadPrompt() {
    try {
      setLoading(true)
      const promptData = await videoApi.getPrompt(promptId!)
      setData(promptData)
      // Initialize editor with latest version
      const latest = promptData.versions.find(
        (v) => v.version_number === promptData.prompt.latest_version_number
      )
      if (latest) {
        setSceneDescription(latest.scene_description || "")
        setMotionTiming(latest.motion_timing || "")
        setStyleTone(latest.style_tone || "")
        setCameraLanguage(latest.camera_language || "")
        setConstraints(latest.constraints || "")
        setNegativeInstructions(latest.negative_instructions || "")
      }
      setHasChanges(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load prompt")
    } finally {
      setLoading(false)
    }
  }

  function generateFullPromptText(): string {
    const parts: string[] = []
    if (sceneDescription) parts.push(`Scene: ${sceneDescription}`)
    if (motionTiming) parts.push(`Motion/Timing: ${motionTiming}`)
    if (styleTone) parts.push(`Style/Tone: ${styleTone}`)
    if (cameraLanguage) parts.push(`Camera: ${cameraLanguage}`)
    if (constraints) parts.push(`Constraints: ${constraints}`)
    if (negativeInstructions) parts.push(`Avoid: ${negativeInstructions}`)
    return parts.join("\n\n")
  }

  async function handleSaveVersion() {
    try {
      setSaving(true)
      await videoApi.createVersion(promptId!, {
        scene_description: sceneDescription || undefined,
        motion_timing: motionTiming || undefined,
        style_tone: styleTone || undefined,
        camera_language: cameraLanguage || undefined,
        constraints: constraints || undefined,
        negative_instructions: negativeInstructions || undefined,
      })
      await loadPrompt()
      setHasChanges(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save version")
    } finally {
      setSaving(false)
    }
  }

  async function handleRollback(versionId: string) {
    try {
      await videoApi.rollbackVersion(promptId!, versionId)
      await loadPrompt()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to rollback")
    }
  }

  async function handleGenerateVariants() {
    try {
      setGeneratingVariants(true)
      await videoApi.generateVariants(promptId!, 5)
      await loadPrompt()
      setActiveTab("versions")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate variants")
    } finally {
      setGeneratingVariants(false)
    }
  }

  async function handlePromoteVariant(versionId: string) {
    try {
      await videoApi.promoteVariant(versionId)
      await loadPrompt()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to promote variant")
    }
  }

  async function handleDeleteVersion(versionId: string) {
    if (!confirm("Delete this draft variant?")) return
    try {
      await videoApi.deleteVersion(versionId)
      await loadPrompt()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete version")
    }
  }

  async function handleAttachOutput(e: React.FormEvent) {
    e.preventDefault()
    if (!attachUrl.trim() || !selectedVersionForOutput) return

    try {
      setAttaching(true)
      await videoApi.attachOutput(selectedVersionForOutput, attachUrl.trim(), attachNotes.trim() || undefined)
      await loadPrompt()
      setShowAttachForm(false)
      setAttachUrl("")
      setAttachNotes("")
      setSelectedVersionForOutput(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to attach output")
    } finally {
      setAttaching(false)
    }
  }

  async function handleScoreOutput(outputId: string, rating: "good" | "bad", reasonTags?: string[]) {
    try {
      await videoApi.scoreOutput(outputId, rating, reasonTags)
      await loadPrompt()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to score output")
    }
  }

  async function handleDeleteOutput(outputId: string) {
    if (!confirm("Delete this output?")) return
    try {
      await videoApi.deleteOutput(outputId)
      await loadPrompt()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete output")
    }
  }

  async function handleCreateShareLink() {
    try {
      setCreatingShare(true)
      const token = await videoApi.createShareToken(promptId!, 7)
      setShareToken(token.token)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create share link")
    } finally {
      setCreatingShare(false)
    }
  }

  function copyShareLink() {
    if (!shareToken) return
    const url = `${window.location.origin}/video/share/${shareToken}`
    navigator.clipboard.writeText(url)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (!data) {
    return (
      <div className="container max-w-5xl py-8">
        <div className="text-center">
          <h2 className="text-xl font-medium mb-2">Prompt not found</h2>
          <Link to="/video">
            <Button variant="outline">Back to Projects</Button>
          </Link>
        </div>
      </div>
    )
  }

  const { prompt, versions, best_version_id } = data
  const draftVariants = versions.filter((v) => v.type === "variant" && v.status === "draft")

  return (
    <div className="container max-w-5xl py-8">
      <div className="mb-6 flex items-center justify-between">
        <Link
          to={`/video/projects/${prompt.project_id}`}
          className="text-sm text-muted-foreground hover:text-foreground inline-flex items-center gap-1"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Project
        </Link>
        <Button variant="outline" size="sm" onClick={() => setShowShareModal(true)}>
          <Share2 className="h-4 w-4 mr-2" />
          Share
        </Button>
      </div>

      {error && (
        <div className="bg-destructive/10 text-destructive px-4 py-3 rounded-md mb-6">
          {error}
          <button onClick={() => setError(null)} className="ml-2 font-medium">
            Dismiss
          </button>
        </div>
      )}

      {/* Header */}
      <Card className="mb-6">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-xl">{prompt.name}</CardTitle>
              {prompt.purpose && (
                <p className="text-muted-foreground mt-1">{prompt.purpose}</p>
              )}
              <div className="flex items-center gap-3 mt-2 text-sm text-muted-foreground">
                {prompt.target_model && <span>Model: {prompt.target_model}</span>}
                <span>Version {prompt.latest_version_number || 1}</span>
              </div>
            </div>
            {best_version_id && (
              <Badge variant="secondary" className="gap-1">
                <Star className="h-3 w-3" />
                Best Version Available
              </Badge>
            )}
          </div>
        </CardHeader>
      </Card>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b">
        <button
          className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors ${
            activeTab === "editor"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
          onClick={() => setActiveTab("editor")}
        >
          Editor
        </button>
        <button
          className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors ${
            activeTab === "versions"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
          onClick={() => setActiveTab("versions")}
        >
          Versions ({versions.length})
        </button>
        <button
          className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors ${
            activeTab === "outputs"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
          onClick={() => setActiveTab("outputs")}
        >
          Outputs
        </button>
      </div>

      {/* Editor Tab */}
      {activeTab === "editor" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Structured Prompt Editor</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="scene">Scene Description</Label>
                  <textarea
                    id="scene"
                    className="w-full min-h-[80px] px-3 py-2 border rounded-md text-sm resize-y"
                    value={sceneDescription}
                    onChange={(e) => {
                      setSceneDescription(e.target.value)
                      setHasChanges(true)
                    }}
                    placeholder="Describe the scene..."
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="motion">Motion / Timing</Label>
                  <textarea
                    id="motion"
                    className="w-full min-h-[60px] px-3 py-2 border rounded-md text-sm resize-y"
                    value={motionTiming}
                    onChange={(e) => {
                      setMotionTiming(e.target.value)
                      setHasChanges(true)
                    }}
                    placeholder="Motion and timing instructions..."
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="style">Style / Tone</Label>
                  <textarea
                    id="style"
                    className="w-full min-h-[60px] px-3 py-2 border rounded-md text-sm resize-y"
                    value={styleTone}
                    onChange={(e) => {
                      setStyleTone(e.target.value)
                      setHasChanges(true)
                    }}
                    placeholder="Visual style and tone..."
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="camera">Camera Language</Label>
                  <textarea
                    id="camera"
                    className="w-full min-h-[60px] px-3 py-2 border rounded-md text-sm resize-y"
                    value={cameraLanguage}
                    onChange={(e) => {
                      setCameraLanguage(e.target.value)
                      setHasChanges(true)
                    }}
                    placeholder="Camera movements and angles..."
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="constraints">Constraints</Label>
                  <textarea
                    id="constraints"
                    className="w-full min-h-[60px] px-3 py-2 border rounded-md text-sm resize-y"
                    value={constraints}
                    onChange={(e) => {
                      setConstraints(e.target.value)
                      setHasChanges(true)
                    }}
                    placeholder="Any constraints or requirements..."
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="negative">Negative Instructions (Avoid)</Label>
                  <textarea
                    id="negative"
                    className="w-full min-h-[60px] px-3 py-2 border rounded-md text-sm resize-y"
                    value={negativeInstructions}
                    onChange={(e) => {
                      setNegativeInstructions(e.target.value)
                      setHasChanges(true)
                    }}
                    placeholder="What to avoid..."
                  />
                </div>
              </CardContent>
            </Card>

            <div className="flex gap-2">
              <Button onClick={handleSaveVersion} disabled={saving || !hasChanges}>
                {saving ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Save className="h-4 w-4 mr-2" />
                )}
                Save as New Version
              </Button>
              <Button
                variant="outline"
                onClick={handleGenerateVariants}
                disabled={generatingVariants}
              >
                {generatingVariants ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Sparkles className="h-4 w-4 mr-2" />
                )}
                Generate Variants
              </Button>
            </div>
          </div>

          <div>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="text-base">Full Prompt Preview</CardTitle>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    navigator.clipboard.writeText(generateFullPromptText())
                  }}
                >
                  <Copy className="h-4 w-4 mr-1" />
                  Copy
                </Button>
              </CardHeader>
              <CardContent>
                <pre className="whitespace-pre-wrap text-sm bg-muted p-4 rounded-md max-h-[500px] overflow-auto">
                  {generateFullPromptText() || "(Empty prompt)"}
                </pre>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* Versions Tab */}
      {activeTab === "versions" && (
        <div className="space-y-4">
          {draftVariants.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Draft Variants</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {draftVariants.map((variant) => (
                  <div
                    key={variant.id}
                    className="border rounded-md p-4"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Badge variant="outline">Variant v{variant.version_number}</Badge>
                        <span className="text-xs text-muted-foreground">
                          {new Date(variant.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handlePromoteVariant(variant.id)}
                        >
                          <Check className="h-4 w-4 mr-1" />
                          Keep
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleDeleteVersion(variant.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                    <pre className="text-xs bg-muted p-3 rounded whitespace-pre-wrap max-h-[200px] overflow-auto">
                      {variant.full_prompt_text || "(Empty)"}
                    </pre>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Version History</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {versions
                  .filter((v) => v.type === "main" || v.status === "active")
                  .map((version) => (
                    <div
                      key={version.id}
                      className={`border rounded-md p-4 ${
                        version.id === best_version_id ? "border-primary" : ""
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">Version {version.version_number}</span>
                          {version.id === best_version_id && (
                            <Badge variant="default" className="gap-1">
                              <Star className="h-3 w-3" />
                              Best
                            </Badge>
                          )}
                          {version.version_number === prompt.latest_version_number && (
                            <Badge variant="secondary">Latest</Badge>
                          )}
                        </div>
                        <div className="flex items-center gap-3">
                          <div className="flex items-center gap-2 text-sm">
                            <span className="text-green-600 flex items-center gap-1">
                              <ThumbsUp className="h-3 w-3" />
                              {version.good_count}
                            </span>
                            <span className="text-red-600 flex items-center gap-1">
                              <ThumbsDown className="h-3 w-3" />
                              {version.bad_count}
                            </span>
                          </div>
                          {version.version_number !== prompt.latest_version_number && (
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => handleRollback(version.id)}
                            >
                              <RotateCcw className="h-4 w-4 mr-1" />
                              Rollback
                            </Button>
                          )}
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => {
                              setSelectedVersionForOutput(version.id)
                              setShowAttachForm(true)
                              setActiveTab("outputs")
                            }}
                          >
                            <LinkIcon className="h-4 w-4 mr-1" />
                            Add Output
                          </Button>
                        </div>
                      </div>
                      <p className="text-xs text-muted-foreground mb-2">
                        {new Date(version.created_at).toLocaleString()}
                      </p>
                      <pre className="text-xs bg-muted p-3 rounded whitespace-pre-wrap max-h-[200px] overflow-auto">
                        {version.full_prompt_text || "(Empty)"}
                      </pre>
                    </div>
                  ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Outputs Tab */}
      {activeTab === "outputs" && (
        <div className="space-y-4">
          {showAttachForm && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Attach Output</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleAttachOutput} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="versionSelect">Select Version</Label>
                    <select
                      id="versionSelect"
                      className="w-full px-3 py-2 border rounded-md text-sm"
                      value={selectedVersionForOutput || ""}
                      onChange={(e) => setSelectedVersionForOutput(e.target.value)}
                    >
                      <option value="">Select a version...</option>
                      {versions
                        .filter((v) => v.type === "main" || v.status === "active")
                        .map((v) => (
                          <option key={v.id} value={v.id}>
                            Version {v.version_number}
                          </option>
                        ))}
                    </select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="outputUrl">Video URL</Label>
                    <Input
                      id="outputUrl"
                      value={attachUrl}
                      onChange={(e) => setAttachUrl(e.target.value)}
                      placeholder="https://..."
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="outputNotes">Notes (optional)</Label>
                    <Input
                      id="outputNotes"
                      value={attachNotes}
                      onChange={(e) => setAttachNotes(e.target.value)}
                      placeholder="Any notes about this output..."
                    />
                  </div>
                  <div className="flex gap-2">
                    <Button
                      type="submit"
                      disabled={attaching || !attachUrl.trim() || !selectedVersionForOutput}
                    >
                      {attaching && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                      Attach Output
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => {
                        setShowAttachForm(false)
                        setAttachUrl("")
                        setAttachNotes("")
                        setSelectedVersionForOutput(null)
                      }}
                    >
                      Cancel
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          )}

          {!showAttachForm && (
            <Button onClick={() => setShowAttachForm(true)}>
              <LinkIcon className="h-4 w-4 mr-2" />
              Attach Output
            </Button>
          )}

          {versions.map((version) => {
            const outputs = (version as VideoPromptVersion & { outputs?: VideoPromptOutput[] })
              .outputs || []
            if (outputs.length === 0) return null

            return (
              <Card key={version.id}>
                <CardHeader>
                  <div className="flex items-center gap-2">
                    <CardTitle className="text-base">Version {version.version_number}</CardTitle>
                    {version.id === best_version_id && (
                      <Badge variant="default" className="gap-1">
                        <Star className="h-3 w-3" />
                        Best
                      </Badge>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  {outputs.map((output: VideoPromptOutput) => (
                    <div key={output.id} className="border rounded-md p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <a
                            href={output.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm text-primary hover:underline flex items-center gap-1"
                          >
                            {output.url.length > 60
                              ? output.url.slice(0, 60) + "..."
                              : output.url}
                            <ExternalLink className="h-3 w-3" />
                          </a>
                          {output.notes && (
                            <p className="text-sm text-muted-foreground mt-1">{output.notes}</p>
                          )}
                          <p className="text-xs text-muted-foreground mt-1">
                            {new Date(output.created_at).toLocaleString()}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          {output.rating ? (
                            <div className="flex items-center gap-2">
                              <Badge
                                variant={output.rating === "good" ? "default" : "destructive"}
                                className="gap-1"
                              >
                                {output.rating === "good" ? (
                                  <ThumbsUp className="h-3 w-3" />
                                ) : (
                                  <ThumbsDown className="h-3 w-3" />
                                )}
                                {output.rating}
                              </Badge>
                              {output.reason_tags && output.reason_tags.length > 0 && (
                                <div className="flex gap-1">
                                  {output.reason_tags.map((tag) => (
                                    <Badge key={tag} variant="outline" className="text-xs">
                                      {tag}
                                    </Badge>
                                  ))}
                                </div>
                              )}
                            </div>
                          ) : (
                            <div className="flex gap-1">
                              <Button
                                size="sm"
                                variant="outline"
                                className="text-green-600"
                                onClick={() => handleScoreOutput(output.id, "good")}
                              >
                                <ThumbsUp className="h-4 w-4" />
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                className="text-red-600"
                                onClick={() => handleScoreOutput(output.id, "bad")}
                              >
                                <ThumbsDown className="h-4 w-4" />
                              </Button>
                            </div>
                          )}
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleDeleteOutput(output.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}

      {/* Share Modal */}
      {showShareModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <Card className="w-full max-w-md mx-4">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Share Prompt</CardTitle>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setShowShareModal(false)
                  setShareToken(null)
                }}
              >
                <X className="h-4 w-4" />
              </Button>
            </CardHeader>
            <CardContent>
              {shareToken ? (
                <div className="space-y-4">
                  <p className="text-sm text-muted-foreground">
                    Share this link to allow read-only access to this prompt. The link expires in 7
                    days.
                  </p>
                  <div className="flex gap-2">
                    <Input
                      readOnly
                      value={`${window.location.origin}/video/share/${shareToken}`}
                      className="flex-1"
                    />
                    <Button onClick={copyShareLink}>
                      {copied ? (
                        <Check className="h-4 w-4" />
                      ) : (
                        <Copy className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <p className="text-sm text-muted-foreground">
                    Create a shareable link that allows read-only access to this prompt and its
                    versions.
                  </p>
                  <Button onClick={handleCreateShareLink} disabled={creatingShare}>
                    {creatingShare && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                    Create Share Link
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
