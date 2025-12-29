import { useState, useRef } from "react"
import { Upload, X, FileText, Image, File, Loader2, Lock } from "lucide-react"
import { Button } from "@/components/ui/button"
import type { UploadedFile } from "@/lib/api"

export interface UploadedFileState {
  file: File
  base64: string | null
  status: "loading" | "ready" | "error"
  error?: string
}

interface FileUploadProps {
  files: UploadedFileState[]
  onFilesChange: (files: UploadedFileState[]) => void
  isPremium: boolean
  maxFiles?: number
  onUpgradeClick?: () => void
}

const ACCEPTED_TYPES = ".pdf,.docx,.doc,.txt,.md,.csv,.json,.py,.js,.ts,.java,.c,.cpp,.rs,.go,.png,.jpg,.jpeg,.gif,.webp"
const MAX_FILE_SIZE = 5 * 1024 * 1024 // 5MB

async function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => {
      const result = reader.result as string
      // Remove data URL prefix (e.g., "data:image/png;base64,")
      const base64 = result.split(",")[1]
      resolve(base64)
    }
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

export function filesToUploadedFiles(files: UploadedFileState[]): UploadedFile[] {
  return files
    .filter(f => f.status === "ready" && f.base64)
    .map(f => ({
      file_name: f.file.name,
      file_data: f.base64!,
      mime_type: f.file.type || null
    }))
}

function getFileIcon(type: string) {
  if (type.startsWith("image/")) return <Image className="h-4 w-4 text-purple-500" />
  if (type === "application/pdf") return <FileText className="h-4 w-4 text-red-500" />
  return <File className="h-4 w-4 text-blue-500" />
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

export function FileUpload({
  files,
  onFilesChange,
  isPremium,
  maxFiles = 5,
  onUpgradeClick
}: FileUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [isDragging, setIsDragging] = useState(false)

  const handleFileSelect = async (selectedFiles: FileList | null) => {
    if (!selectedFiles) return

    const newFiles: UploadedFileState[] = [...files]

    for (const file of Array.from(selectedFiles)) {
      if (newFiles.length >= maxFiles) break

      // Check size
      if (file.size > MAX_FILE_SIZE) {
        newFiles.push({
          file,
          base64: null,
          status: "error",
          error: "File exceeds 5MB limit"
        })
        continue
      }

      // Add as loading
      const newFile: UploadedFileState = {
        file,
        base64: null,
        status: "loading"
      }
      newFiles.push(newFile)
    }

    onFilesChange(newFiles)

    // Convert to base64 in the background
    // Use a local copy that we update and pass to onFilesChange
    let currentFiles = [...newFiles]
    for (const f of newFiles) {
      if (f.status === "loading") {
        try {
          const base64 = await fileToBase64(f.file)
          currentFiles = currentFiles.map((pf: UploadedFileState) =>
            pf.file === f.file ? { ...pf, base64, status: "ready" as const } : pf
          )
          onFilesChange(currentFiles)
        } catch {
          currentFiles = currentFiles.map((pf: UploadedFileState) =>
            pf.file === f.file ? { ...pf, status: "error" as const, error: "Failed to read file" } : pf
          )
          onFilesChange(currentFiles)
        }
      }
    }

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  const removeFile = (index: number) => {
    onFilesChange(files.filter((_, i) => i !== index))
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    if (isPremium) setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    if (isPremium) {
      handleFileSelect(e.dataTransfer.files)
    }
  }

  if (!isPremium) {
    return (
      <div className="p-4 border border-dashed border-muted-foreground/30 rounded-lg bg-muted/20 text-center">
        <Lock className="h-6 w-6 mx-auto mb-2 text-muted-foreground" />
        <p className="text-sm text-muted-foreground mb-2">
          File upload is available for Premium and Pro users
        </p>
        {onUpgradeClick && (
          <Button variant="link" size="sm" onClick={onUpgradeClick} className="text-purple-500">
            Upgrade to unlock
          </Button>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <div
        className={`p-4 border-2 border-dashed rounded-lg text-center cursor-pointer transition-colors ${
          isDragging
            ? "border-purple-500 bg-purple-50 dark:bg-purple-950/20"
            : "border-muted-foreground/30 hover:border-purple-400"
        }`}
        onClick={() => fileInputRef.current?.click()}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <Upload className={`h-6 w-6 mx-auto mb-2 ${isDragging ? "text-purple-500" : "text-muted-foreground"}`} />
        <p className="text-sm text-muted-foreground">
          Drop files here or click to upload
        </p>
        <p className="text-xs text-muted-foreground mt-1">
          PDF, Word, images, code files (max 5MB, up to {maxFiles} files)
        </p>
        <input
          ref={fileInputRef}
          type="file"
          accept={ACCEPTED_TYPES}
          multiple
          className="hidden"
          onChange={(e) => handleFileSelect(e.target.files)}
        />
      </div>

      {files.length > 0 && (
        <div className="space-y-2">
          {files.map((f, i) => (
            <div
              key={i}
              className={`flex items-center gap-2 p-2 rounded-lg border ${
                f.status === "error"
                  ? "bg-red-50 dark:bg-red-950/20 border-red-200 dark:border-red-800"
                  : "bg-muted/50 border-transparent"
              }`}
            >
              {f.status === "loading" ? (
                <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
              ) : (
                getFileIcon(f.file.type)
              )}
              <span className="text-sm flex-1 truncate">{f.file.name}</span>
              <span className="text-xs text-muted-foreground">
                {formatFileSize(f.file.size)}
              </span>
              {f.status === "error" && (
                <span className="text-xs text-red-500">{f.error}</span>
              )}
              {f.status === "ready" && (
                <span className="text-xs text-green-500">Ready</span>
              )}
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0 hover:bg-red-100 dark:hover:bg-red-900/30"
                onClick={(e) => {
                  e.stopPropagation()
                  removeFile(i)
                }}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
