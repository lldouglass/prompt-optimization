import { useState, useRef, useEffect } from "react"
import { Camera, Video, Sparkles, Copy, Check, Loader2, ArrowRight, AlertCircle, MessageSquare, Wrench, Upload, X, Image, Bookmark, FolderPlus } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { sessionApi, connectMediaAgentWebSocket, type MediaAgentResult, type ToolCallInfo, type PendingQuestion, type UploadedFile, type Folder } from "@/lib/api"
import { track } from "@/lib/analytics"

const API_BASE = import.meta.env.VITE_API_URL || ""

const ASPECT_RATIOS = [
  { value: "1:1", label: "1:1 Square" },
  { value: "16:9", label: "16:9 Landscape" },
  { value: "9:16", label: "9:16 Portrait" },
  { value: "4:3", label: "4:3 Standard" },
  { value: "21:9", label: "21:9 Ultrawide" },
]

export function MediaOptimizerPage() {
  // Media type selection
  const [mediaType, setMediaType] = useState<"photo" | "video">("photo")

  // Input fields
  const [taskDescription, setTaskDescription] = useState("")
  const [existingPrompt, setExistingPrompt] = useState("")
  const [aspectRatio, setAspectRatio] = useState<string>("")

  // Logo upload
  const [logoUrl, setLogoUrl] = useState<string | null>(null)
  const [logoFile, setLogoFile] = useState<File | null>(null)
  const [logoUploading, setLogoUploading] = useState(false)
  const [logoError, setLogoError] = useState<string | null>(null)
  const logoInputRef = useRef<HTMLInputElement>(null)

  // Agent state
  const [isOptimizing, setIsOptimizing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [progressMessage, setProgressMessage] = useState("")
  const [toolCalls, setToolCalls] = useState<ToolCallInfo[]>([])
  const [agentQuestion, setAgentQuestion] = useState<PendingQuestion | null>(null)
  const [agentAnswer, setAgentAnswer] = useState("")

  // Result state
  const [result, setResult] = useState<MediaAgentResult | null>(null)
  const [copied, setCopied] = useState<"prompt" | "negative" | "params" | null>(null)

  // Save to Library state
  const [showSaveForm, setShowSaveForm] = useState(false)
  const [saveName, setSaveName] = useState("")
  const [saveFolder, setSaveFolder] = useState("")
  const [newFolderName, setNewFolderName] = useState("")
  const [folders, setFolders] = useState<Folder[]>([])
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  // WebSocket ref
  const wsRef = useRef<{ sendAnswer: (id: string, answer: string) => void; close: () => void } | null>(null)
  const resultRef = useRef<HTMLDivElement>(null)

  // Handle logo file upload to Cloudinary
  const handleLogoUpload = async (file: File) => {
    setLogoUploading(true)
    setLogoError(null)
    setLogoFile(file)

    try {
      const formData = new FormData()
      formData.append("file", file)

      const res = await fetch(`${API_BASE}/uploads/image`, {
        method: "POST",
        credentials: "include",
        body: formData,
      })

      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail || "Failed to upload image")
      }

      const { url } = await res.json()
      setLogoUrl(url)
    } catch (err) {
      setLogoError(err instanceof Error ? err.message : "Upload failed")
      setLogoFile(null)
    } finally {
      setLogoUploading(false)
    }
  }

  const handleLogoRemove = () => {
    setLogoUrl(null)
    setLogoFile(null)
    setLogoError(null)
    if (logoInputRef.current) {
      logoInputRef.current.value = ""
    }
  }

  // Convert logo file to base64 for vision analysis
  const getLogoAsUploadedFile = async (): Promise<UploadedFile | null> => {
    if (!logoFile) return null

    return new Promise((resolve) => {
      const reader = new FileReader()
      reader.onload = () => {
        const result = reader.result as string
        const base64 = result.split(",")[1]
        resolve({
          file_name: logoFile.name,
          file_data: base64,
          mime_type: logoFile.type || null,
        })
      }
      reader.onerror = () => resolve(null)
      reader.readAsDataURL(logoFile)
    })
  }

  const handleOptimize = async () => {
    if (!taskDescription.trim()) return

    setIsOptimizing(true)
    setError(null)
    setResult(null)
    setProgressMessage("Starting optimization...")
    setToolCalls([])
    setAgentQuestion(null)

    try {
      // Get logo file as base64 for vision analysis
      const logoUploadedFile = await getLogoAsUploadedFile()
      const uploadedFiles = logoUploadedFile ? [logoUploadedFile] : undefined

      // Start the agent session (using generic model since prompts are model-agnostic)
      const session = await sessionApi.startMediaAgentOptimization(
        existingPrompt,
        taskDescription,
        mediaType,
        "generic",
        aspectRatio || undefined,
        logoUrl || undefined,
        uploadedFiles
      )

      // Connect WebSocket
      const ws = connectMediaAgentWebSocket(session.session_id, {
        onProgress: (_step, message) => {
          setProgressMessage(message)
        },
        onToolCalled: (tool, args, resultSummary) => {
          setToolCalls(prev => [...prev, { tool, args, result_summary: resultSummary }])
        },
        onQuestion: (questionId, question, reason, options) => {
          setAgentQuestion({ question_id: questionId, question, reason, options })
          setProgressMessage("Waiting for your answer...")
        },
        onCompleted: (completedResult) => {
          setResult(completedResult)
          setIsOptimizing(false)
          setProgressMessage("")
          wsRef.current = null

          // Scroll to result
          setTimeout(() => {
            resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" })
          }, 100)

          track("media_agent_optimization_completed", {
            media_type: mediaType,
            had_existing_prompt: !!existingPrompt,
          })
        },
        onError: (errorMsg) => {
          setError(errorMsg)
          setIsOptimizing(false)
          setProgressMessage("")
          wsRef.current = null
        },
        onClose: () => {
          if (isOptimizing && !result) {
            setError("Connection closed unexpectedly")
            setIsOptimizing(false)
          }
          wsRef.current = null
        },
      })

      wsRef.current = ws
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start optimization")
      setIsOptimizing(false)
    }
  }

  const handleSubmitAnswer = () => {
    if (!agentQuestion || !agentAnswer.trim() || !wsRef.current) return

    wsRef.current.sendAnswer(agentQuestion.question_id, agentAnswer)
    setAgentQuestion(null)
    setAgentAnswer("")
    setProgressMessage("Processing your answer...")
  }

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      wsRef.current?.close()
    }
  }, [])

  const copyToClipboard = (text: string, type: "prompt" | "negative" | "params") => {
    navigator.clipboard.writeText(text)
    setCopied(type)
    setTimeout(() => setCopied(null), 2000)
  }

  // Load folders when showing save form
  const handleShowSaveForm = async () => {
    setShowSaveForm(true)
    setSaveName(taskDescription.slice(0, 100))
    try {
      const { folders } = await sessionApi.listFolders()
      setFolders(folders)
    } catch (err) {
      console.error("Failed to load folders:", err)
    }
  }

  // Save to library
  const handleSaveToLibrary = async () => {
    if (!result) return
    setSaving(true)
    try {
      const folderToUse = newFolderName.trim() || saveFolder || undefined
      await sessionApi.saveMediaOptimization(
        result,
        taskDescription,
        saveName || undefined,
        folderToUse,
        aspectRatio || undefined
      )
      setSaved(true)
      setShowSaveForm(false)
      track("media_optimization_saved", {
        media_type: mediaType,
        has_folder: !!folderToUse,
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save")
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="container py-8 max-w-4xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold flex items-center gap-3">
          {mediaType === "photo" ? (
            <Camera className="h-8 w-8 text-primary" />
          ) : (
            <Video className="h-8 w-8 text-primary" />
          )}
          Media Prompt Optimizer
        </h1>
        <p className="text-muted-foreground mt-2">
          Create optimized prompts for AI image and video generation using our intelligent agent.
        </p>
      </div>

      <div className="space-y-6">
      {/* Input Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5" />
            Smart Optimization
          </CardTitle>
          <CardDescription>
            Our AI agent will analyze your request and ask clarifying questions to create the best prompt for AI image and video generation.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Media Type Toggle */}
          <div className="flex gap-2">
            <Button
              variant={mediaType === "photo" ? "default" : "outline"}
              onClick={() => setMediaType("photo")}
              className="flex-1"
            >
              <Camera className="h-4 w-4 mr-2" />
              Photo
            </Button>
            <Button
              variant={mediaType === "video" ? "default" : "outline"}
              onClick={() => setMediaType("video")}
              className="flex-1"
            >
              <Video className="h-4 w-4 mr-2" />
              Video
            </Button>
          </div>

          {/* Task Description */}
          <div className="space-y-2">
            <Label htmlFor="task">What do you want to create? *</Label>
            <Textarea
              id="task"
              placeholder={mediaType === "photo"
                ? "e.g., A portrait of a woman in soft golden hour lighting, cinematic style"
                : "e.g., A slow dolly-in shot of a chef plating food in a steamy kitchen"
              }
              value={taskDescription}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setTaskDescription(e.target.value)}
              rows={3}
            />
          </div>

          {/* Existing Prompt (Optional) */}
          <div className="space-y-2">
            <Label htmlFor="existing">Existing prompt to improve (optional)</Label>
            <Textarea
              id="existing"
              placeholder="Paste an existing prompt to optimize it..."
              value={existingPrompt}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setExistingPrompt(e.target.value)}
              rows={2}
            />
          </div>

          {/* Aspect Ratio */}
          <div className="space-y-2">
            <Label>Aspect Ratio (optional)</Label>
            <div className="flex flex-wrap gap-2">
              {ASPECT_RATIOS.map((ar) => (
                <Button
                  key={ar.value}
                  variant={aspectRatio === ar.value ? "default" : "outline"}
                  size="sm"
                  onClick={() => setAspectRatio(aspectRatio === ar.value ? "" : ar.value)}
                >
                  {ar.label}
                </Button>
              ))}
            </div>
          </div>

          {/* Logo Upload (Photo only, Midjourney recommended) */}
          {mediaType === "photo" && (
            <div className="space-y-2">
              <Label>Logo / Brand Image (optional)</Label>
              <p className="text-sm text-muted-foreground">
                Upload your logo to include it in the prompt. Works best with Midjourney.
              </p>

              {!logoUrl && !logoUploading && (
                <div
                  className="border-2 border-dashed rounded-lg p-6 text-center cursor-pointer hover:border-primary/50 transition-colors"
                  onClick={() => logoInputRef.current?.click()}
                >
                  <input
                    ref={logoInputRef}
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={(e) => {
                      const file = e.target.files?.[0]
                      if (file) handleLogoUpload(file)
                    }}
                  />
                  <Upload className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                  <p className="text-sm text-muted-foreground">
                    Click to upload logo (PNG, JPG, WebP)
                  </p>
                </div>
              )}

              {logoUploading && (
                <div className="flex items-center gap-2 p-4 bg-muted rounded-lg">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span className="text-sm">Uploading...</span>
                </div>
              )}

              {logoUrl && logoFile && (
                <div className="flex items-center gap-3 p-3 bg-muted rounded-lg">
                  <Image className="h-5 w-5 text-primary" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{logoFile.name}</p>
                    <p className="text-xs text-green-600 truncate">
                      Uploaded to Cloudinary
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleLogoRemove}
                    className="flex-shrink-0"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              )}

              {logoError && (
                <p className="text-sm text-destructive">{logoError}</p>
              )}
            </div>
          )}

          {/* Optimize Button */}
          <Button
            onClick={handleOptimize}
            disabled={isOptimizing || !taskDescription.trim()}
            className="w-full"
            size="lg"
          >
            {isOptimizing ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Optimizing...
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4 mr-2" />
                Generate Optimized Prompt
              </>
            )}
          </Button>

          {/* Error Display */}
          {error && (
            <div className="flex items-center gap-2 p-3 bg-destructive/10 text-destructive rounded-lg">
              <AlertCircle className="h-4 w-4 flex-shrink-0" />
              <span className="text-sm">{error}</span>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Progress/Agent Interaction */}
      {isOptimizing && (
        <Card>
          <CardContent className="pt-6 space-y-4">
            {/* Progress Message */}
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              {progressMessage}
            </div>

            {/* Tool Calls */}
            {toolCalls.length > 0 && (
              <div className="space-y-2">
                <div className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Agent Actions
                </div>
                {toolCalls.map((tc, i) => (
                  <div key={i} className="flex items-start gap-2 text-sm p-2 bg-muted/50 rounded">
                    <Wrench className="h-4 w-4 mt-0.5 text-muted-foreground" />
                    <div>
                      <span className="font-medium">{tc.tool}</span>
                      {tc.result_summary && (
                        <span className="text-muted-foreground"> - {tc.result_summary}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Question from Agent */}
            {agentQuestion && (
              <div className="space-y-3 p-4 bg-primary/5 border border-primary/20 rounded-lg">
                <div className="flex items-start gap-2">
                  <MessageSquare className="h-5 w-5 text-primary mt-0.5" />
                  <div>
                    <div className="font-medium">{agentQuestion.question}</div>
                    <div className="text-sm text-muted-foreground mt-1">{agentQuestion.reason}</div>
                  </div>
                </div>

                {/* Multiple choice options */}
                {agentQuestion.options && agentQuestion.options.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {agentQuestion.options.map((option, index) => (
                      <Button
                        key={index}
                        variant={agentAnswer === option ? "default" : "outline"}
                        size="sm"
                        onClick={() => setAgentAnswer(option)}
                        className="transition-all"
                      >
                        {option}
                      </Button>
                    ))}
                    <Button
                      variant={agentAnswer && !agentQuestion.options.includes(agentAnswer) ? "default" : "outline"}
                      size="sm"
                      onClick={() => setAgentAnswer("")}
                      className="transition-all"
                    >
                      Other...
                    </Button>
                  </div>
                )}

                {/* Text input for "Other" or when no options */}
                {(!agentQuestion.options || agentQuestion.options.length === 0 || (agentAnswer === "" || !agentQuestion.options.includes(agentAnswer))) && (
                  <div className="flex gap-2">
                    <Input
                      placeholder="Type your answer..."
                      value={agentQuestion.options?.includes(agentAnswer) ? "" : agentAnswer}
                      onChange={(e) => setAgentAnswer(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && handleSubmitAnswer()}
                      autoFocus={agentQuestion.options && agentQuestion.options.length > 0}
                    />
                  </div>
                )}

                {/* Submit button */}
                <div className="flex justify-end">
                  <Button onClick={handleSubmitAnswer} disabled={!agentAnswer.trim()}>
                    Submit Answer
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Results */}
      {result && (
        <div ref={resultRef} className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Optimization Results</span>
                <div className="flex items-center gap-2 text-sm font-normal">
                  <span className="text-muted-foreground">Score:</span>
                  <span className={result.optimized_score >= 7 ? "text-green-600" : result.optimized_score >= 5 ? "text-yellow-600" : "text-red-600"}>
                    {result.original_score.toFixed(1)} → {result.optimized_score.toFixed(1)}
                  </span>
                  {result.optimized_score > result.original_score && (
                    <span className="text-green-600">
                      (+{(result.optimized_score - result.original_score).toFixed(1)})
                    </span>
                  )}
                </div>
              </CardTitle>
              <CardDescription className="flex items-center justify-between">
                <span>Optimized {mediaType} prompt</span>
                <Button
                  variant={saved ? "outline" : "default"}
                  size="sm"
                  onClick={handleShowSaveForm}
                  disabled={saved || showSaveForm}
                >
                  {saved ? (
                    <>
                      <Check className="h-4 w-4 mr-2 text-green-600" />
                      Saved
                    </>
                  ) : (
                    <>
                      <Bookmark className="h-4 w-4 mr-2" />
                      Save to Library
                    </>
                  )}
                </Button>
              </CardDescription>
            </CardHeader>

            {/* Save to Library Form */}
            {showSaveForm && (
              <div className="px-6 pb-4 border-b">
                <div className="bg-muted/50 rounded-lg p-4 space-y-4">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium flex items-center gap-2">
                      <Bookmark className="h-4 w-4" />
                      Save to Library
                    </h4>
                    <Button variant="ghost" size="sm" onClick={() => setShowSaveForm(false)}>
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="save-name">Name</Label>
                      <Input
                        id="save-name"
                        placeholder="Enter a name for this prompt"
                        value={saveName}
                        onChange={(e) => setSaveName(e.target.value)}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="save-folder">Folder</Label>
                      <div className="flex gap-2">
                        <select
                          id="save-folder"
                          className="flex-1 h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                          value={saveFolder}
                          onChange={(e) => {
                            setSaveFolder(e.target.value)
                            setNewFolderName("")
                          }}
                          disabled={!!newFolderName}
                        >
                          <option value="">No folder</option>
                          {folders.map(f => (
                            <option key={f.name} value={f.name}>{f.name} ({f.count})</option>
                          ))}
                        </select>
                      </div>
                      <div className="flex items-center gap-2">
                        <FolderPlus className="h-4 w-4 text-muted-foreground" />
                        <Input
                          placeholder="Or create new folder..."
                          value={newFolderName}
                          onChange={(e) => {
                            setNewFolderName(e.target.value)
                            if (e.target.value) setSaveFolder("")
                          }}
                          className="flex-1"
                        />
                      </div>
                    </div>
                  </div>
                  <div className="flex justify-end gap-2">
                    <Button variant="outline" onClick={() => setShowSaveForm(false)}>
                      Cancel
                    </Button>
                    <Button onClick={handleSaveToLibrary} disabled={saving}>
                      {saving ? (
                        <>
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          Saving...
                        </>
                      ) : (
                        "Save"
                      )}
                    </Button>
                  </div>
                </div>
              </div>
            )}

            <CardContent className="space-y-6">
              {/* Optimized Prompt */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label>Optimized Prompt</Label>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => copyToClipboard(result.optimized_prompt, "prompt")}
                  >
                    {copied === "prompt" ? (
                      <Check className="h-4 w-4 text-green-600" />
                    ) : (
                      <Copy className="h-4 w-4" />
                    )}
                  </Button>
                </div>
                <div className="p-4 bg-muted rounded-lg font-mono text-sm whitespace-pre-wrap">
                  {result.optimized_prompt}
                </div>
              </div>

              {/* Parameters */}
              {result.parameters && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label>Parameters</Label>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => copyToClipboard(result.parameters!, "params")}
                    >
                      {copied === "params" ? (
                        <Check className="h-4 w-4 text-green-600" />
                      ) : (
                        <Copy className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                  <div className="p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg font-mono text-sm">
                    {result.parameters}
                  </div>
                </div>
              )}

              {/* Improvements */}
              {result.improvements.length > 0 && (
                <div className="space-y-2">
                  <Label>Improvements Made</Label>
                  <ul className="space-y-1">
                    {result.improvements.map((imp, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm">
                        <Check className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                        {imp}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Reasoning */}
              {result.reasoning && (
                <div className="space-y-2">
                  <Label>Why These Changes</Label>
                  <p className="text-sm text-muted-foreground">{result.reasoning}</p>
                </div>
              )}

              {/* Tips */}
              {result.tips && result.tips.length > 0 && (
                <div className="space-y-2">
                  <Label>Tips</Label>
                  <ul className="space-y-1">
                    {result.tips.map((tip, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                        <Sparkles className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                        {tip}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
      </div>
    </div>
  )
}
