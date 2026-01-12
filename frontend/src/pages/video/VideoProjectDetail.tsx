import { useState, useEffect } from "react"
import { Link, useParams, useNavigate } from "react-router-dom"
import { videoApi, type VideoProject, type VideoPrompt } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { ArrowLeft, Plus, FileText, ChevronRight, Loader2, Trash2, Pencil } from "lucide-react"

export function VideoProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const [project, setProject] = useState<VideoProject | null>(null)
  const [prompts, setPrompts] = useState<VideoPrompt[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [createName, setCreateName] = useState("")
  const [createPurpose, setCreatePurpose] = useState("")
  const [createTargetModel, setCreateTargetModel] = useState("")
  const [creating, setCreating] = useState(false)
  const [editing, setEditing] = useState(false)
  const [editName, setEditName] = useState("")
  const [editDescription, setEditDescription] = useState("")
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    if (projectId) {
      loadProject()
    }
  }, [projectId])

  async function loadProject() {
    try {
      setLoading(true)
      const [projectData, promptsData] = await Promise.all([
        videoApi.getProject(projectId!),
        videoApi.listPrompts(projectId!),
      ])
      setProject(projectData)
      setPrompts(promptsData.prompts)
      setEditName(projectData.name)
      setEditDescription(projectData.description || "")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load project")
    } finally {
      setLoading(false)
    }
  }

  async function handleCreatePrompt(e: React.FormEvent) {
    e.preventDefault()
    if (!createName.trim()) return

    try {
      setCreating(true)
      const prompt = await videoApi.createPrompt(projectId!, {
        name: createName.trim(),
        purpose: createPurpose.trim() || undefined,
        target_model: createTargetModel.trim() || undefined,
      })
      navigate(`/video/prompts/${prompt.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create prompt")
    } finally {
      setCreating(false)
    }
  }

  async function handleUpdateProject(e: React.FormEvent) {
    e.preventDefault()
    if (!editName.trim()) return

    try {
      const updated = await videoApi.updateProject(projectId!, {
        name: editName.trim(),
        description: editDescription.trim() || undefined,
      })
      setProject(updated)
      setEditing(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update project")
    }
  }

  async function handleDeleteProject() {
    if (!confirm("Are you sure you want to delete this project? All prompts will be deleted.")) {
      return
    }

    try {
      setDeleting(true)
      await videoApi.deleteProject(projectId!)
      navigate("/video")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete project")
      setDeleting(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (!project) {
    return (
      <div className="container max-w-4xl py-8">
        <div className="text-center">
          <h2 className="text-xl font-medium mb-2">Project not found</h2>
          <Link to="/video">
            <Button variant="outline">Back to Projects</Button>
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="container max-w-4xl py-8">
      <div className="mb-6">
        <Link to="/video" className="text-sm text-muted-foreground hover:text-foreground inline-flex items-center gap-1">
          <ArrowLeft className="h-4 w-4" />
          Back to Projects
        </Link>
      </div>

      {error && (
        <div className="bg-destructive/10 text-destructive px-4 py-3 rounded-md mb-6">
          {error}
        </div>
      )}

      <Card className="mb-6">
        <CardHeader className="flex flex-row items-start justify-between">
          {editing ? (
            <form onSubmit={handleUpdateProject} className="flex-1 space-y-4">
              <div className="space-y-2">
                <Label htmlFor="editName">Project Name</Label>
                <Input
                  id="editName"
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  autoFocus
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="editDescription">Description</Label>
                <Input
                  id="editDescription"
                  value={editDescription}
                  onChange={(e) => setEditDescription(e.target.value)}
                />
              </div>
              <div className="flex gap-2">
                <Button type="submit" size="sm">Save</Button>
                <Button type="button" variant="outline" size="sm" onClick={() => setEditing(false)}>
                  Cancel
                </Button>
              </div>
            </form>
          ) : (
            <>
              <div>
                <CardTitle className="text-xl">{project.name}</CardTitle>
                {project.description && (
                  <p className="text-muted-foreground mt-1">{project.description}</p>
                )}
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={() => setEditing(true)}>
                  <Pencil className="h-4 w-4 mr-1" />
                  Edit
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleDeleteProject}
                  disabled={deleting}
                  className="text-destructive hover:text-destructive"
                >
                  {deleting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
                </Button>
              </div>
            </>
          )}
        </CardHeader>
      </Card>

      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-medium">Prompts</h2>
        <Button onClick={() => setShowCreateForm(true)} size="sm">
          <Plus className="h-4 w-4 mr-2" />
          New Prompt
        </Button>
      </div>

      {showCreateForm && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-base">Create New Prompt</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreatePrompt} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="promptName">Prompt Name</Label>
                <Input
                  id="promptName"
                  value={createName}
                  onChange={(e) => setCreateName(e.target.value)}
                  placeholder="e.g., Hero Product Shot"
                  autoFocus
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="purpose">Purpose (optional)</Label>
                <Input
                  id="purpose"
                  value={createPurpose}
                  onChange={(e) => setCreatePurpose(e.target.value)}
                  placeholder="What is this prompt for?"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="targetModel">Target Model (optional)</Label>
                <Input
                  id="targetModel"
                  value={createTargetModel}
                  onChange={(e) => setCreateTargetModel(e.target.value)}
                  placeholder="e.g., Runway, Pika, Sora"
                />
              </div>
              <div className="flex gap-2">
                <Button type="submit" disabled={creating || !createName.trim()}>
                  {creating && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                  Create Prompt
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setShowCreateForm(false)
                    setCreateName("")
                    setCreatePurpose("")
                    setCreateTargetModel("")
                  }}
                >
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {prompts.length === 0 && !showCreateForm ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <FileText className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium mb-2">No prompts yet</h3>
            <p className="text-muted-foreground text-center mb-4">
              Create your first video prompt to start optimizing
            </p>
            <Button onClick={() => setShowCreateForm(true)} size="sm">
              <Plus className="h-4 w-4 mr-2" />
              Create Prompt
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {prompts.map((prompt) => (
            <Link key={prompt.id} to={`/video/prompts/${prompt.id}`}>
              <Card className="hover:bg-muted/50 transition-colors cursor-pointer">
                <CardContent className="flex items-center justify-between py-4">
                  <div className="flex items-center gap-4">
                    <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                      <FileText className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <h3 className="font-medium">{prompt.name}</h3>
                      {prompt.purpose && (
                        <p className="text-sm text-muted-foreground line-clamp-1">
                          {prompt.purpose}
                        </p>
                      )}
                      <div className="flex items-center gap-3 text-xs text-muted-foreground mt-1">
                        {prompt.target_model && <span>{prompt.target_model}</span>}
                        <span>{prompt.version_count} version{prompt.version_count !== 1 ? "s" : ""}</span>
                      </div>
                    </div>
                  </div>
                  <ChevronRight className="h-5 w-5 text-muted-foreground" />
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
