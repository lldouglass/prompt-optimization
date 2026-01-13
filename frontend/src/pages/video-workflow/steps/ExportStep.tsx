import { useState } from "react"
import { Loader2, Download, Copy, Check, FileJson, FileText, Bookmark, ExternalLink } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { videoWorkflowApi, type VideoWorkflowDetail } from "@/lib/api"

interface ExportStepProps {
  workflow: VideoWorkflowDetail | null
}

export function ExportStep({ workflow }: ExportStepProps) {
  const [isExporting, setIsExporting] = useState(false)
  const [isCreatingTemplate, setIsCreatingTemplate] = useState(false)
  const [templateName, setTemplateName] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [copiedPrompt, setCopiedPrompt] = useState<number | null>(null)
  const [templateCreated, setTemplateCreated] = useState(false)

  const handleExport = async (format: "json" | "markdown") => {
    if (!workflow) return

    setIsExporting(true)
    setError(null)

    try {
      const result = await videoWorkflowApi.export(workflow.id, format)

      // Create and download file
      const blob = new Blob([result.content], {
        type: format === "json" ? "application/json" : "text/markdown",
      })
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = result.filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to export")
    } finally {
      setIsExporting(false)
    }
  }

  const handleCreateTemplate = async () => {
    if (!workflow || !templateName.trim()) return

    setIsCreatingTemplate(true)
    setError(null)

    try {
      await videoWorkflowApi.createTemplate(workflow.id, templateName)
      setTemplateCreated(true)
      setTemplateName("")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create template")
    } finally {
      setIsCreatingTemplate(false)
    }
  }

  const copyPromptToClipboard = (text: string, index: number) => {
    navigator.clipboard.writeText(text)
    setCopiedPrompt(index)
    setTimeout(() => setCopiedPrompt(null), 2000)
  }

  if (!workflow) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-center text-muted-foreground">
            No workflow data available
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Export Options */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Download className="h-5 w-5" />
            Export Workflow
          </CardTitle>
          <CardDescription>
            Download your complete workflow as JSON or Markdown.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-4">
            <Button
              onClick={() => handleExport("json")}
              disabled={isExporting}
              className="flex-1"
            >
              {isExporting ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <FileJson className="h-4 w-4 mr-2" />
              )}
              Export JSON
            </Button>
            <Button
              variant="outline"
              onClick={() => handleExport("markdown")}
              disabled={isExporting}
              className="flex-1"
            >
              {isExporting ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <FileText className="h-4 w-4 mr-2" />
              )}
              Export Markdown
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Copy Prompts */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Copy className="h-5 w-5" />
            Copy Prompts
          </CardTitle>
          <CardDescription>
            Copy individual prompts to use in Sora 2 or other tools.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {workflow.prompt_pack?.prompts ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {workflow.prompt_pack.prompts.map((prompt, index) => (
                <Button
                  key={prompt.shot_id}
                  variant="outline"
                  onClick={() => copyPromptToClipboard(prompt.prompt_text, index)}
                  className="justify-between h-auto py-3"
                >
                  <span className="text-left">
                    Shot {index + 1}
                    <span className="text-xs text-muted-foreground ml-2">
                      ({prompt.sora_params.duration}s)
                    </span>
                  </span>
                  {copiedPrompt === index ? (
                    <Check className="h-4 w-4 text-green-600" />
                  ) : (
                    <Copy className="h-4 w-4" />
                  )}
                </Button>
              ))}
            </div>
          ) : (
            <p className="text-center text-muted-foreground py-4">
              No prompts generated yet
            </p>
          )}
        </CardContent>
      </Card>

      {/* Create Template */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bookmark className="h-5 w-5" />
            Save as Template
          </CardTitle>
          <CardDescription>
            Create a reusable template from this workflow (keeps brief, continuity, and shot plan).
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {templateCreated ? (
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <Check className="h-6 w-6 text-green-600 mx-auto mb-2" />
              <p className="font-medium text-green-900">Template created!</p>
              <p className="text-sm text-green-700">
                You can find it in the Templates section.
              </p>
            </div>
          ) : (
            <div className="flex gap-4">
              <div className="flex-1">
                <Label htmlFor="templateName" className="sr-only">
                  Template Name
                </Label>
                <Input
                  id="templateName"
                  value={templateName}
                  onChange={e => setTemplateName(e.target.value)}
                  placeholder="Template name..."
                />
              </div>
              <Button
                onClick={handleCreateTemplate}
                disabled={isCreatingTemplate || !templateName.trim()}
              >
                {isCreatingTemplate ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Bookmark className="h-4 w-4 mr-2" />
                )}
                Create Template
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Workflow Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div className="p-4 bg-muted rounded-lg">
              <div className="text-2xl font-bold">
                {workflow.shot_plan?.shots?.length || 0}
              </div>
              <div className="text-sm text-muted-foreground">Shots</div>
            </div>
            <div className="p-4 bg-muted rounded-lg">
              <div className="text-2xl font-bold">
                {workflow.prompt_pack?.prompts?.length || 0}
              </div>
              <div className="text-sm text-muted-foreground">Prompts</div>
            </div>
            <div className="p-4 bg-muted rounded-lg">
              <div className="text-2xl font-bold">
                {workflow.qa_score?.overall_score || "--"}
              </div>
              <div className="text-sm text-muted-foreground">QA Score</div>
            </div>
            <div className="p-4 bg-muted rounded-lg">
              <div className="text-2xl font-bold">
                {workflow.brief?.duration_seconds || "--"}s
              </div>
              <div className="text-sm text-muted-foreground">Duration</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <div className="bg-destructive/10 text-destructive rounded-lg p-4">
          {error}
        </div>
      )}

      {/* Next Steps */}
      <Card>
        <CardHeader>
          <CardTitle>Next Steps</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center gap-3 p-3 bg-muted rounded-lg">
            <ExternalLink className="h-5 w-5 text-muted-foreground" />
            <div>
              <p className="font-medium">Use in Sora 2</p>
              <p className="text-sm text-muted-foreground">
                Copy each prompt and paste it into Sora 2's interface.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3 p-3 bg-muted rounded-lg">
            <FileText className="h-5 w-5 text-muted-foreground" />
            <div>
              <p className="font-medium">Share with Team</p>
              <p className="text-sm text-muted-foreground">
                Export as Markdown to share the shot plan with your video team.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3 p-3 bg-muted rounded-lg">
            <Bookmark className="h-5 w-5 text-muted-foreground" />
            <div>
              <p className="font-medium">Reuse for Similar Projects</p>
              <p className="text-sm text-muted-foreground">
                Save as a template to quickly start similar video projects.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
