import { useState, useEffect, useMemo } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/lib/auth"
import { createAuthenticatedAgentApi } from "@/lib/api"
import type { SavedOptimization } from "@/lib/api"
import { Loader2, Library, ChevronDown, ChevronUp, Copy, Check } from "lucide-react"

export function PromptLibraryPage() {
  const { rawApiKey } = useAuth()
  const [optimizations, setOptimizations] = useState<SavedOptimization[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [copiedField, setCopiedField] = useState<string | null>(null)

  const authAgentApi = useMemo(
    () => (rawApiKey ? createAuthenticatedAgentApi(rawApiKey) : null),
    [rawApiKey]
  )

  useEffect(() => {
    if (authAgentApi) {
      loadOptimizations()
    }
  }, [authAgentApi])

  const loadOptimizations = async () => {
    if (!authAgentApi) return
    setLoading(true)
    try {
      const result = await authAgentApi.listOptimizations(50, 0)
      setOptimizations(result.optimizations)
      setTotal(result.total)
    } catch (error) {
      console.error("Failed to load optimizations:", error)
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = (text: string, fieldId: string) => {
    navigator.clipboard.writeText(text)
    setCopiedField(fieldId)
    setTimeout(() => setCopiedField(null), 2000)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Library className="h-8 w-8 text-primary" />
            Prompt Library
          </h1>
          <p className="text-muted-foreground mt-1">
            {total} saved prompt{total !== 1 ? "s" : ""}
          </p>
        </div>
        <Button onClick={loadOptimizations} variant="outline">
          Refresh
        </Button>
      </div>

      {optimizations.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Library className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium">Your prompt library is empty</h3>
            <p className="text-muted-foreground mt-1">
              Optimize prompts and save them to build your library.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {optimizations.map((opt) => (
            <Card key={opt.id}>
              <div
                className="px-4 py-3 cursor-pointer hover:bg-muted/50 transition-colors flex items-center justify-between"
                onClick={() => setExpandedId(expandedId === opt.id ? null : opt.id)}
              >
                <h3 className="font-medium">{opt.task_description}</h3>
                <Button variant="ghost" size="sm">
                  {expandedId === opt.id ? (
                    <ChevronUp className="h-4 w-4" />
                  ) : (
                    <ChevronDown className="h-4 w-4" />
                  )}
                </Button>
              </div>

              {expandedId === opt.id && (
                <CardContent className="border-t pt-4">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    {/* Original Prompt */}
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="text-sm font-medium text-muted-foreground">Original</h4>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-7 px-2"
                          onClick={(e) => {
                            e.stopPropagation()
                            copyToClipboard(opt.original_prompt, `${opt.id}-original`)
                          }}
                        >
                          {copiedField === `${opt.id}-original` ? (
                            <Check className="h-3 w-3 text-green-600" />
                          ) : (
                            <Copy className="h-3 w-3" />
                          )}
                        </Button>
                      </div>
                      <div className="bg-muted p-3 rounded-lg text-sm font-mono whitespace-pre-wrap max-h-80 overflow-auto">
                        {opt.original_prompt}
                      </div>
                    </div>

                    {/* Optimized Prompt */}
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="text-sm font-medium text-muted-foreground">Optimized</h4>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-7 px-2"
                          onClick={(e) => {
                            e.stopPropagation()
                            copyToClipboard(opt.optimized_prompt, `${opt.id}-optimized`)
                          }}
                        >
                          {copiedField === `${opt.id}-optimized` ? (
                            <Check className="h-3 w-3 text-green-600" />
                          ) : (
                            <Copy className="h-3 w-3" />
                          )}
                        </Button>
                      </div>
                      <div className="bg-green-50 dark:bg-green-950/20 p-3 rounded-lg text-sm font-mono whitespace-pre-wrap max-h-80 overflow-auto border border-green-200 dark:border-green-800">
                        {opt.optimized_prompt}
                      </div>
                    </div>
                  </div>
                </CardContent>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
