import { useState, useEffect } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { sessionApi } from "@/lib/api"
import type { SavedOptimization, Folder } from "@/lib/api"
import {
  Loader2,
  Library,
  ChevronDown,
  ChevronUp,
  Copy,
  Check,
  Folder as FolderIcon,
  Camera,
  Video,
  FileText,
  Search,
  Edit,
  Trash,
  X,
  Save,
  RefreshCw,
} from "lucide-react"

type MediaTypeFilter = "all" | "text" | "photo" | "video"

export function PromptLibraryPage() {
  // Data state
  const [optimizations, setOptimizations] = useState<SavedOptimization[]>([])
  const [folders, setFolders] = useState<Folder[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)

  // Filter state
  const [selectedFolder, setSelectedFolder] = useState<string | null>(null)
  const [mediaTypeFilter, setMediaTypeFilter] = useState<MediaTypeFilter>("all")
  const [searchQuery, setSearchQuery] = useState("")
  const [debouncedSearch, setDebouncedSearch] = useState("")

  // UI state
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editName, setEditName] = useState("")
  const [editPrompt, setEditPrompt] = useState("")
  const [editFolder, setEditFolder] = useState("")
  const [savingEdit, setSavingEdit] = useState(false)
  const [copiedField, setCopiedField] = useState<string | null>(null)
  const [deletingId, setDeletingId] = useState<string | null>(null)

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery)
    }, 300)
    return () => clearTimeout(timer)
  }, [searchQuery])

  // Load data when filters change
  useEffect(() => {
    loadData()
  }, [selectedFolder, mediaTypeFilter, debouncedSearch])

  const loadData = async () => {
    setLoading(true)
    try {
      const [optimizationsResult, foldersResult] = await Promise.all([
        sessionApi.listOptimizations(100, 0, {
          folder: selectedFolder ?? undefined,
          media_type: mediaTypeFilter === "all" ? undefined : mediaTypeFilter,
          search: debouncedSearch || undefined,
        }),
        sessionApi.listFolders(),
      ])
      setOptimizations(optimizationsResult.optimizations)
      setTotal(optimizationsResult.total)
      setFolders(foldersResult.folders)
    } catch (error) {
      console.error("Failed to load data:", error)
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = (text: string, fieldId: string) => {
    navigator.clipboard.writeText(text)
    setCopiedField(fieldId)
    setTimeout(() => setCopiedField(null), 2000)
  }

  // Edit handlers
  const startEditing = (opt: SavedOptimization) => {
    setEditingId(opt.id)
    setEditName(opt.name || opt.task_description)
    setEditPrompt(opt.optimized_prompt)
    setEditFolder(opt.folder || "")
    setExpandedId(opt.id)
  }

  const cancelEditing = () => {
    setEditingId(null)
    setEditName("")
    setEditPrompt("")
    setEditFolder("")
  }

  const saveEdit = async () => {
    if (!editingId) return
    setSavingEdit(true)
    try {
      await sessionApi.updateOptimization(editingId, {
        name: editName,
        optimized_prompt: editPrompt,
        folder: editFolder || undefined,
      })
      setEditingId(null)
      loadData()
    } catch (error) {
      console.error("Failed to save:", error)
    } finally {
      setSavingEdit(false)
    }
  }

  const deleteOptimization = async (id: string) => {
    if (!confirm("Are you sure you want to delete this prompt?")) return
    setDeletingId(id)
    try {
      await sessionApi.deleteOptimization(id)
      loadData()
    } catch (error) {
      console.error("Failed to delete:", error)
    } finally {
      setDeletingId(null)
    }
  }

  // Get icon for media type
  const getTypeIcon = (opt: SavedOptimization) => {
    if (opt.media_type === "photo") return <Camera className="h-4 w-4 text-blue-600" />
    if (opt.media_type === "video") return <Video className="h-4 w-4 text-purple-600" />
    return <FileText className="h-4 w-4 text-gray-600" />
  }

  // Get display name
  const getDisplayName = (opt: SavedOptimization) => {
    return opt.name || opt.task_description
  }

  return (
    <div className="p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Library className="h-8 w-8 text-primary" />
            Prompt Library
          </h1>
          <p className="text-muted-foreground mt-1">
            {total} saved prompt{total !== 1 ? "s" : ""}
          </p>
        </div>
        <Button onClick={loadData} variant="outline" size="sm">
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Filters Row */}
      <div className="flex flex-wrap gap-4 items-center mb-6">
        {/* Search */}
        <div className="relative flex-1 min-w-[200px] max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search prompts..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>

        {/* Media Type Filter */}
        <div className="flex gap-1">
          {[
            { value: "all" as const, label: "All", icon: null },
            { value: "text" as const, label: "Text", icon: FileText },
            { value: "photo" as const, label: "Photo", icon: Camera },
            { value: "video" as const, label: "Video", icon: Video },
          ].map(({ value, label, icon: Icon }) => (
            <Button
              key={value}
              variant={mediaTypeFilter === value ? "default" : "outline"}
              size="sm"
              onClick={() => setMediaTypeFilter(value)}
            >
              {Icon && <Icon className="h-4 w-4 mr-1" />}
              {label}
            </Button>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex gap-6">
        {/* Folders Sidebar */}
        <div className="w-48 shrink-0 space-y-1">
          <div className="font-medium text-sm text-muted-foreground mb-2 px-2">Folders</div>
          <Button
            variant={selectedFolder === null ? "secondary" : "ghost"}
            className="w-full justify-start"
            size="sm"
            onClick={() => setSelectedFolder(null)}
          >
            <FolderIcon className="h-4 w-4 mr-2" />
            All Prompts
          </Button>
          <Button
            variant={selectedFolder === "" ? "secondary" : "ghost"}
            className="w-full justify-start"
            size="sm"
            onClick={() => setSelectedFolder("")}
          >
            <FolderIcon className="h-4 w-4 mr-2" />
            Unfiled
          </Button>
          {folders.map((folder) => (
            <Button
              key={folder.name}
              variant={selectedFolder === folder.name ? "secondary" : "ghost"}
              className="w-full justify-between"
              size="sm"
              onClick={() => setSelectedFolder(folder.name)}
            >
              <span className="flex items-center truncate">
                <FolderIcon className="h-4 w-4 mr-2 shrink-0" />
                <span className="truncate">{folder.name}</span>
              </span>
              <span className="text-xs text-muted-foreground ml-2">{folder.count}</span>
            </Button>
          ))}
        </div>

        {/* Prompts List */}
        <div className="flex-1 space-y-3">
          {loading ? (
            <div className="flex justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : optimizations.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <Library className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium">No prompts found</h3>
                <p className="text-muted-foreground mt-1">
                  {searchQuery || selectedFolder !== null
                    ? "Try adjusting your filters"
                    : "Save optimized prompts to build your library"}
                </p>
              </CardContent>
            </Card>
          ) : (
            optimizations.map((opt) => (
              <Card key={opt.id}>
                {/* Card header */}
                <div
                  className="px-4 py-3 cursor-pointer hover:bg-muted/50 transition-colors flex items-center justify-between"
                  onClick={() => setExpandedId(expandedId === opt.id ? null : opt.id)}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    {getTypeIcon(opt)}
                    <div className="min-w-0">
                      <h3 className="font-medium truncate">{getDisplayName(opt)}</h3>
                      <div className="flex gap-2 text-xs text-muted-foreground">
                        {opt.target_model && <span>{opt.target_model}</span>}
                        {opt.folder && (
                          <span className="flex items-center gap-1">
                            <FolderIcon className="h-3 w-3" />
                            {opt.folder}
                          </span>
                        )}
                        <span>{new Date(opt.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-8 w-8 p-0"
                      onClick={(e) => {
                        e.stopPropagation()
                        startEditing(opt)
                      }}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-8 w-8 p-0 text-destructive hover:text-destructive"
                      onClick={(e) => {
                        e.stopPropagation()
                        deleteOptimization(opt.id)
                      }}
                      disabled={deletingId === opt.id}
                    >
                      {deletingId === opt.id ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Trash className="h-4 w-4" />
                      )}
                    </Button>
                    {expandedId === opt.id ? (
                      <ChevronUp className="h-4 w-4 ml-2" />
                    ) : (
                      <ChevronDown className="h-4 w-4 ml-2" />
                    )}
                  </div>
                </div>

                {/* Expanded content */}
                {expandedId === opt.id && (
                  <CardContent className="border-t pt-4 space-y-4">
                    {/* Editing mode */}
                    {editingId === opt.id ? (
                      <div className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <Label>Name</Label>
                            <Input
                              value={editName}
                              onChange={(e) => setEditName(e.target.value)}
                              placeholder="Prompt name"
                            />
                          </div>
                          <div className="space-y-2">
                            <Label>Folder</Label>
                            <select
                              className="w-full h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
                              value={editFolder}
                              onChange={(e) => setEditFolder(e.target.value)}
                            >
                              <option value="">No folder</option>
                              {folders.map((f) => (
                                <option key={f.name} value={f.name}>
                                  {f.name}
                                </option>
                              ))}
                            </select>
                          </div>
                        </div>
                        <div className="space-y-2">
                          <Label>Optimized Prompt</Label>
                          <Textarea
                            value={editPrompt}
                            onChange={(e) => setEditPrompt(e.target.value)}
                            rows={6}
                            className="font-mono text-sm"
                          />
                        </div>
                        <div className="flex gap-2">
                          <Button onClick={saveEdit} disabled={savingEdit}>
                            {savingEdit ? (
                              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                            ) : (
                              <Save className="h-4 w-4 mr-2" />
                            )}
                            Save Changes
                          </Button>
                          <Button variant="outline" onClick={cancelEditing}>
                            <X className="h-4 w-4 mr-2" />
                            Cancel
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <>
                        {/* Display mode */}
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                          {/* Original Prompt */}
                          <div>
                            <div className="flex items-center justify-between mb-2">
                              <Label className="text-muted-foreground">Original</Label>
                              <Button
                                variant="ghost"
                                size="sm"
                                className="h-7 px-2"
                                onClick={() => copyToClipboard(opt.original_prompt, `${opt.id}-original`)}
                              >
                                {copiedField === `${opt.id}-original` ? (
                                  <Check className="h-3 w-3 text-green-600" />
                                ) : (
                                  <Copy className="h-3 w-3" />
                                )}
                              </Button>
                            </div>
                            <div className="bg-muted p-3 rounded-lg text-sm font-mono whitespace-pre-wrap max-h-60 overflow-auto">
                              {opt.original_prompt || "(No original prompt)"}
                            </div>
                          </div>

                          {/* Optimized Prompt */}
                          <div>
                            <div className="flex items-center justify-between mb-2">
                              <Label className="text-muted-foreground">Optimized</Label>
                              <Button
                                variant="ghost"
                                size="sm"
                                className="h-7 px-2"
                                onClick={() => copyToClipboard(opt.optimized_prompt, `${opt.id}-optimized`)}
                              >
                                {copiedField === `${opt.id}-optimized` ? (
                                  <Check className="h-3 w-3 text-green-600" />
                                ) : (
                                  <Copy className="h-3 w-3" />
                                )}
                              </Button>
                            </div>
                            <div className="bg-green-50 dark:bg-green-950/20 p-3 rounded-lg text-sm font-mono whitespace-pre-wrap max-h-60 overflow-auto border border-green-200 dark:border-green-800">
                              {opt.optimized_prompt}
                            </div>
                          </div>
                        </div>

                        {/* Media-specific fields */}
                        {opt.negative_prompt && (
                          <div>
                            <div className="flex items-center justify-between mb-2">
                              <Label className="text-muted-foreground">Negative Prompt</Label>
                              <Button
                                variant="ghost"
                                size="sm"
                                className="h-7 px-2"
                                onClick={() => copyToClipboard(opt.negative_prompt!, `${opt.id}-negative`)}
                              >
                                {copiedField === `${opt.id}-negative` ? (
                                  <Check className="h-3 w-3 text-green-600" />
                                ) : (
                                  <Copy className="h-3 w-3" />
                                )}
                              </Button>
                            </div>
                            <div className="bg-red-50 dark:bg-red-950/20 p-3 rounded-lg text-sm font-mono whitespace-pre-wrap border border-red-200 dark:border-red-800">
                              {opt.negative_prompt}
                            </div>
                          </div>
                        )}

                        {opt.parameters && (
                          <div>
                            <div className="flex items-center justify-between mb-2">
                              <Label className="text-muted-foreground">Parameters</Label>
                              <Button
                                variant="ghost"
                                size="sm"
                                className="h-7 px-2"
                                onClick={() => copyToClipboard(opt.parameters!, `${opt.id}-params`)}
                              >
                                {copiedField === `${opt.id}-params` ? (
                                  <Check className="h-3 w-3 text-green-600" />
                                ) : (
                                  <Copy className="h-3 w-3" />
                                )}
                              </Button>
                            </div>
                            <div className="bg-blue-50 dark:bg-blue-950/20 p-3 rounded-lg text-sm font-mono border border-blue-200 dark:border-blue-800">
                              {opt.parameters}
                            </div>
                          </div>
                        )}

                        {/* Tips */}
                        {opt.tips && opt.tips.length > 0 && (
                          <div>
                            <Label className="text-muted-foreground">Tips</Label>
                            <ul className="mt-2 space-y-1 text-sm">
                              {opt.tips.map((tip, i) => (
                                <li key={i} className="flex items-start gap-2">
                                  <span className="text-primary">•</span>
                                  {tip}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {/* Improvements */}
                        {opt.improvements && opt.improvements.length > 0 && (
                          <div>
                            <Label className="text-muted-foreground">Improvements Made</Label>
                            <ul className="mt-2 space-y-1 text-sm">
                              {opt.improvements.map((imp, i) => (
                                <li key={i} className="flex items-start gap-2">
                                  <Check className="h-4 w-4 text-green-600 shrink-0 mt-0.5" />
                                  {imp}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </>
                    )}
                  </CardContent>
                )}
              </Card>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
