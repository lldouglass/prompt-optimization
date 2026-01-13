import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { Plus, Film, Loader2, Trash2, Copy, MoreVertical, FileText, Bookmark } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { videoWorkflowApi, type VideoWorkflow } from "@/lib/api"
import { WORKFLOW_STEPS } from "@/types/video-workflow"

export function VideoWorkflowListPage() {
  const navigate = useNavigate()
  const [workflows, setWorkflows] = useState<VideoWorkflow[]>([])
  const [templates, setTemplates] = useState<VideoWorkflow[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [deleteId, setDeleteId] = useState<string | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const [workflowsData, templatesData] = await Promise.all([
        videoWorkflowApi.list(),
        videoWorkflowApi.listTemplates(),
      ])
      setWorkflows(workflowsData)
      setTemplates(templatesData)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load workflows")
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreateNew = async () => {
    try {
      const workflow = await videoWorkflowApi.create("New Video Workflow")
      navigate(`/video-workflow/${workflow.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create workflow")
    }
  }

  const handleCreateFromTemplate = async (templateId: string, templateName: string) => {
    try {
      const workflow = await videoWorkflowApi.createFromTemplate(templateId, `${templateName} Copy`)
      navigate(`/video-workflow/${workflow.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create from template")
    }
  }

  const handleDelete = async () => {
    if (!deleteId) return
    setIsDeleting(true)
    try {
      await videoWorkflowApi.delete(deleteId)
      setWorkflows(workflows.filter(w => w.id !== deleteId))
      setTemplates(templates.filter(t => t.id !== deleteId))
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete workflow")
    } finally {
      setIsDeleting(false)
      setDeleteId(null)
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "draft":
        return <Badge variant="secondary">Draft</Badge>
      case "in_progress":
        return <Badge variant="default">In Progress</Badge>
      case "completed":
        return <Badge className="bg-green-600">Completed</Badge>
      default:
        return <Badge variant="outline">{status}</Badge>
    }
  }

  const getStepName = (step: number) => {
    return WORKFLOW_STEPS[step - 1]?.name || `Step ${step}`
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="container py-8 max-w-6xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Film className="h-8 w-8" />
            Video Workflows
          </h1>
          <p className="text-muted-foreground mt-1">
            Create structured video prompts for Sora 2 and other AI video tools.
          </p>
        </div>
        <Button onClick={handleCreateNew}>
          <Plus className="h-4 w-4 mr-2" />
          New Workflow
        </Button>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-destructive/10 text-destructive rounded-lg p-4 mb-6">
          {error}
        </div>
      )}

      {/* Templates Section */}
      {templates.length > 0 && (
        <section className="mb-8">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Bookmark className="h-5 w-5" />
            Templates
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {templates.map(template => (
              <Card
                key={template.id}
                className="hover:border-primary/50 transition-colors cursor-pointer"
                onClick={() => handleCreateFromTemplate(template.id, template.name)}
              >
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-lg">{template.name}</CardTitle>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild onClick={(e: React.MouseEvent) => e.stopPropagation()}>
                        <Button variant="ghost" size="icon" className="h-8 w-8">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem
                          onClick={(e: React.MouseEvent) => {
                            e.stopPropagation()
                            handleCreateFromTemplate(template.id, template.name)
                          }}
                        >
                          <Copy className="h-4 w-4 mr-2" />
                          Use Template
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          className="text-destructive"
                          onClick={(e: React.MouseEvent) => {
                            e.stopPropagation()
                            setDeleteId(template.id)
                          }}
                        >
                          <Trash2 className="h-4 w-4 mr-2" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                  <CardDescription>
                    Click to create a new workflow from this template
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <FileText className="h-4 w-4" />
                    Template
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>
      )}

      {/* Workflows Section */}
      <section>
        <h2 className="text-xl font-semibold mb-4">Your Workflows</h2>
        {workflows.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <Film className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <h3 className="text-lg font-medium mb-2">No workflows yet</h3>
              <p className="text-muted-foreground mb-4">
                Create your first video workflow to get started.
              </p>
              <Button onClick={handleCreateNew}>
                <Plus className="h-4 w-4 mr-2" />
                Create Workflow
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {workflows.map(workflow => (
              <Card
                key={workflow.id}
                className="hover:border-primary/50 transition-colors cursor-pointer"
                onClick={() => navigate(`/video-workflow/${workflow.id}`)}
              >
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-lg">{workflow.name}</CardTitle>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild onClick={(e: React.MouseEvent) => e.stopPropagation()}>
                        <Button variant="ghost" size="icon" className="h-8 w-8">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem
                          onClick={(e: React.MouseEvent) => {
                            e.stopPropagation()
                            navigate(`/video-workflow/${workflow.id}`)
                          }}
                        >
                          <FileText className="h-4 w-4 mr-2" />
                          Open
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          className="text-destructive"
                          onClick={(e: React.MouseEvent) => {
                            e.stopPropagation()
                            setDeleteId(workflow.id)
                          }}
                        >
                          <Trash2 className="h-4 w-4 mr-2" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    {getStatusBadge(workflow.status)}
                    <span className="text-sm text-muted-foreground">
                      {getStepName(workflow.current_step)}
                    </span>
                  </div>
                  <div className="mt-3">
                    <div className="flex gap-1">
                      {WORKFLOW_STEPS.map((_, index) => (
                        <div
                          key={index}
                          className={`h-1 flex-1 rounded-full ${
                            index < workflow.current_step
                              ? "bg-primary"
                              : "bg-muted"
                          }`}
                        />
                      ))}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      Step {workflow.current_step} of {WORKFLOW_STEPS.length}
                    </p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </section>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={!!deleteId} onOpenChange={() => setDeleteId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Workflow</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this workflow? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              disabled={isDeleting}
            >
              {isDeleting ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                "Delete"
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
