import { useState, useEffect } from "react"
import { useParams } from "react-router-dom"
import { videoApi, type SharedVideoPrompt, type VideoPromptOutput } from "@/lib/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  ThumbsUp,
  ThumbsDown,
  Loader2,
  Star,
  ExternalLink,
  Lock,
} from "lucide-react"

export function VideoPromptSharePage() {
  const { token } = useParams<{ token: string }>()
  const [data, setData] = useState<SharedVideoPrompt | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (token) {
      loadSharedPrompt()
    }
  }, [token])

  async function loadSharedPrompt() {
    try {
      setLoading(true)
      const promptData = await videoApi.getSharedPrompt(token!)
      setData(promptData)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load shared prompt")
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Card className="max-w-md mx-4">
          <CardContent className="pt-6 text-center">
            <Lock className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h2 className="text-xl font-medium mb-2">Access Denied</h2>
            <p className="text-muted-foreground">
              {error || "This share link is invalid, expired, or has been revoked."}
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  const { prompt, versions, outputs, best_version_id } = data

  // Group outputs by version
  const outputsByVersion: Record<string, VideoPromptOutput[]> = {}
  for (const output of outputs) {
    if (!outputsByVersion[output.version_id]) {
      outputsByVersion[output.version_id] = []
    }
    outputsByVersion[output.version_id].push(output)
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container max-w-4xl py-8">
        {/* Header */}
        <div className="mb-6 flex items-center gap-2">
          <Badge variant="secondary" className="gap-1">
            <Lock className="h-3 w-3" />
            Read-only View
          </Badge>
        </div>

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
                  <span>{versions.length} version{versions.length !== 1 ? "s" : ""}</span>
                </div>
              </div>
              {best_version_id && (
                <Badge variant="default" className="gap-1">
                  <Star className="h-3 w-3" />
                  Best Version Available
                </Badge>
              )}
            </div>
          </CardHeader>
        </Card>

        {/* Versions */}
        <h2 className="text-lg font-medium mb-4">Versions</h2>
        <div className="space-y-4">
          {versions
            .filter((v) => v.type === "main" || v.status === "active")
            .map((version) => {
              const versionOutputs = outputsByVersion[version.id] || []

              return (
                <Card
                  key={version.id}
                  className={version.id === best_version_id ? "border-primary" : ""}
                >
                  <CardHeader>
                    <div className="flex items-center justify-between">
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
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {new Date(version.created_at).toLocaleString()}
                    </p>
                  </CardHeader>
                  <CardContent>
                    <pre className="text-sm bg-muted p-4 rounded whitespace-pre-wrap max-h-[300px] overflow-auto mb-4">
                      {version.full_prompt_text || "(Empty prompt)"}
                    </pre>

                    {versionOutputs.length > 0 && (
                      <div className="space-y-2">
                        <h4 className="text-sm font-medium">Outputs</h4>
                        {versionOutputs.map((output) => (
                          <div
                            key={output.id}
                            className="border rounded p-3 flex items-start justify-between"
                          >
                            <div>
                              <a
                                href={output.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-sm text-primary hover:underline flex items-center gap-1"
                              >
                                {output.url.length > 50
                                  ? output.url.slice(0, 50) + "..."
                                  : output.url}
                                <ExternalLink className="h-3 w-3" />
                              </a>
                              {output.notes && (
                                <p className="text-xs text-muted-foreground mt-1">
                                  {output.notes}
                                </p>
                              )}
                            </div>
                            {output.rating && (
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
                                    {output.reason_tags.map((tag: string) => (
                                      <Badge key={tag} variant="outline" className="text-xs">
                                        {tag}
                                      </Badge>
                                    ))}
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              )
            })}
        </div>

        <div className="mt-8 text-center text-sm text-muted-foreground">
          Shared via <a href="/" className="text-primary hover:underline">Clarynt</a>
        </div>
      </div>
    </div>
  )
}
