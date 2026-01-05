import { useState, useEffect, useRef } from "react"
import { motion, AnimatePresence } from "motion/react"
import { Badge } from "@/components/ui/badge"
import { Check, RefreshCw, Play, Film } from "lucide-react"

// Prompts for the demo
const BEFORE_PROMPT = "a dog running on the beach"

const AFTER_PROMPT_LINES = [
  { text: "Golden retriever running on sandy beach at sunset,", isHighlight: false },
  { text: "slow-motion tracking shot from low angle,", isHighlight: true },
  { text: "soft golden hour lighting, waves splashing,", isHighlight: true },
  { text: "cinematic 24fps, shallow depth of field --ar 16:9", isHighlight: true },
]

const BEFORE_ISSUES = [
  "No style or mood guidance",
  "Missing camera movement",
  "No lighting specified",
  "Generic subject description",
]

const AFTER_IMPROVEMENTS = [
  "Clear subject and action",
  "Cinematic lighting defined",
  "Camera movement specified",
  "Model-specific parameters",
]

type Phase =
  | "play-before-video"
  | "show-before-prompt"
  | "transforming"
  | "play-after-video"
  | "show-after-prompt"
  | "complete"

interface VideoComparisonDemoProps {
  beforeVideoSrc?: string
  afterVideoSrc?: string
}

export function VideoComparisonDemo({
  beforeVideoSrc,
  afterVideoSrc,
}: VideoComparisonDemoProps) {
  const [phase, setPhase] = useState<Phase>("play-before-video")
  const [displayedText, setDisplayedText] = useState("")
  const [afterLineIndex, setAfterLineIndex] = useState(0)
  const [afterCharIndex, setAfterCharIndex] = useState(0)
  const [visibleIssues, setVisibleIssues] = useState(0)
  const [visibleImprovements, setVisibleImprovements] = useState(0)
  const [showCursor, setShowCursor] = useState(true)
  const [videoProgress, setVideoProgress] = useState(0)

  const beforeVideoRef = useRef<HTMLVideoElement>(null)
  const afterVideoRef = useRef<HTMLVideoElement>(null)

  // Cursor blink effect
  useEffect(() => {
    const interval = setInterval(() => {
      setShowCursor((prev) => !prev)
    }, 530)
    return () => clearInterval(interval)
  }, [])

  // Phase: play-before-video - Show video for ~3 seconds then transition
  useEffect(() => {
    if (phase !== "play-before-video") return

    // Simulate video playing (3 seconds for placeholder, or actual video duration)
    const videoDuration = beforeVideoSrc ? 5000 : 3000
    const progressInterval = setInterval(() => {
      setVideoProgress((prev) => Math.min(prev + 100 / (videoDuration / 50), 100))
    }, 50)

    const timeout = setTimeout(() => {
      setPhase("show-before-prompt")
      setVideoProgress(0)
    }, videoDuration)

    return () => {
      clearTimeout(timeout)
      clearInterval(progressInterval)
    }
  }, [phase, beforeVideoSrc])

  // Phase: show-before-prompt - Type prompt then show issues
  useEffect(() => {
    if (phase !== "show-before-prompt") return

    if (displayedText.length < BEFORE_PROMPT.length) {
      const timeout = setTimeout(() => {
        setDisplayedText(BEFORE_PROMPT.slice(0, displayedText.length + 1))
      }, 50)
      return () => clearTimeout(timeout)
    } else if (visibleIssues < BEFORE_ISSUES.length) {
      const timeout = setTimeout(() => {
        setVisibleIssues((prev) => prev + 1)
      }, 300)
      return () => clearTimeout(timeout)
    } else {
      const timeout = setTimeout(() => setPhase("transforming"), 1500)
      return () => clearTimeout(timeout)
    }
  }, [phase, displayedText, visibleIssues])

  // Phase: transforming - Brief pause
  useEffect(() => {
    if (phase !== "transforming") return
    const timeout = setTimeout(() => {
      setPhase("play-after-video")
    }, 800)
    return () => clearTimeout(timeout)
  }, [phase])

  // Phase: play-after-video - Show optimized video
  useEffect(() => {
    if (phase !== "play-after-video") return

    const videoDuration = afterVideoSrc ? 5000 : 3000
    const progressInterval = setInterval(() => {
      setVideoProgress((prev) => Math.min(prev + 100 / (videoDuration / 50), 100))
    }, 50)

    const timeout = setTimeout(() => {
      setPhase("show-after-prompt")
      setVideoProgress(0)
    }, videoDuration)

    return () => {
      clearTimeout(timeout)
      clearInterval(progressInterval)
    }
  }, [phase, afterVideoSrc])

  // Phase: show-after-prompt - Type optimized prompt line by line
  useEffect(() => {
    if (phase !== "show-after-prompt") return

    if (afterLineIndex < AFTER_PROMPT_LINES.length) {
      const currentLine = AFTER_PROMPT_LINES[afterLineIndex].text

      if (afterCharIndex < currentLine.length) {
        const timeout = setTimeout(() => {
          setAfterCharIndex((prev) => prev + 1)
        }, 20)
        return () => clearTimeout(timeout)
      } else {
        const timeout = setTimeout(() => {
          setAfterLineIndex((prev) => prev + 1)
          setAfterCharIndex(0)
        }, 100)
        return () => clearTimeout(timeout)
      }
    } else if (visibleImprovements < AFTER_IMPROVEMENTS.length) {
      const timeout = setTimeout(() => {
        setVisibleImprovements((prev) => prev + 1)
      }, 300)
      return () => clearTimeout(timeout)
    } else {
      const timeout = setTimeout(() => setPhase("complete"), 1000)
      return () => clearTimeout(timeout)
    }
  }, [phase, afterLineIndex, afterCharIndex, visibleImprovements])

  const resetAnimation = () => {
    setPhase("play-before-video")
    setDisplayedText("")
    setAfterLineIndex(0)
    setAfterCharIndex(0)
    setVisibleIssues(0)
    setVisibleImprovements(0)
    setVideoProgress(0)
  }

  const isBeforePhase = phase === "play-before-video" || phase === "show-before-prompt"
  const isTransforming = phase === "transforming"
  const isAfterPhase =
    phase === "play-after-video" ||
    phase === "show-after-prompt" ||
    phase === "complete"

  // Placeholder video component
  const VideoPlaceholder = ({
    type,
    progress,
  }: {
    type: "before" | "after"
    progress?: number
  }) => (
    <div
      className={`relative aspect-video w-full rounded-xl overflow-hidden ${
        type === "before"
          ? "bg-gradient-to-br from-red-900/20 via-red-800/10 to-red-900/20"
          : "bg-gradient-to-br from-green-900/20 via-green-800/10 to-green-900/20"
      }`}
    >
      {/* Animated gradient overlay */}
      <motion.div
        className="absolute inset-0 opacity-30"
        animate={{
          background: [
            `linear-gradient(45deg, ${type === "before" ? "#7f1d1d" : "#14532d"} 0%, transparent 50%)`,
            `linear-gradient(225deg, ${type === "before" ? "#7f1d1d" : "#14532d"} 0%, transparent 50%)`,
            `linear-gradient(45deg, ${type === "before" ? "#7f1d1d" : "#14532d"} 0%, transparent 50%)`,
          ],
        }}
        transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
      />

      {/* Center content */}
      <div className="absolute inset-0 flex flex-col items-center justify-center gap-3">
        <Film className={`h-12 w-12 ${type === "before" ? "text-red-400/50" : "text-green-400/50"}`} />
        <span className={`text-sm font-medium ${type === "before" ? "text-red-400/70" : "text-green-400/70"}`}>
          {type === "before" ? "Before Optimization" : "After Optimization"}
        </span>
        <span className="text-xs text-muted-foreground">Video placeholder</span>
      </div>

      {/* Progress bar */}
      {progress !== undefined && progress > 0 && (
        <div className="absolute bottom-0 left-0 right-0 h-1 bg-black/20">
          <motion.div
            className={`h-full ${type === "before" ? "bg-red-400" : "bg-green-400"}`}
            style={{ width: `${progress}%` }}
          />
        </div>
      )}

      {/* Play indicator */}
      <div className="absolute bottom-3 right-3">
        <div className={`flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium ${
          type === "before"
            ? "bg-red-500/20 text-red-300"
            : "bg-green-500/20 text-green-300"
        }`}>
          <Play className="h-3 w-3 fill-current" />
          Playing
        </div>
      </div>
    </div>
  )

  // Actual video component (when src is provided)
  const VideoPlayer = ({
    src,
    type,
    videoRef,
    progress,
  }: {
    src: string
    type: "before" | "after"
    videoRef: React.RefObject<HTMLVideoElement | null>
    progress?: number
  }) => (
    <div className="relative aspect-video w-full rounded-xl overflow-hidden bg-black">
      <video
        ref={videoRef}
        src={src}
        className="w-full h-full object-cover"
        autoPlay
        muted
        playsInline
      />
      {/* Progress bar */}
      {progress !== undefined && progress > 0 && (
        <div className="absolute bottom-0 left-0 right-0 h-1 bg-black/20">
          <motion.div
            className={`h-full ${type === "before" ? "bg-red-400" : "bg-green-400"}`}
            style={{ width: `${progress}%` }}
          />
        </div>
      )}
    </div>
  )

  return (
    <div className="max-w-4xl mx-auto">
      <div className="relative">
        <AnimatePresence mode="wait">
          {/* Before Section */}
          {(isBeforePhase || isTransforming) && (
            <motion.div
              key="before"
              initial={{ opacity: 0, y: 20 }}
              animate={{
                opacity: isTransforming ? 0 : 1,
                y: 0,
                scale: isTransforming ? 0.95 : 1,
              }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.4 }}
              className="space-y-6"
            >
              {/* Video */}
              {phase === "play-before-video" && (
                beforeVideoSrc ? (
                  <VideoPlayer
                    src={beforeVideoSrc}
                    type="before"
                    videoRef={beforeVideoRef}
                    progress={videoProgress}
                  />
                ) : (
                  <VideoPlaceholder type="before" progress={videoProgress} />
                )
              )}

              {/* Prompt Card */}
              {phase === "show-before-prompt" && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-card rounded-2xl border-2 border-red-200 dark:border-red-800 p-8 relative"
                >
                  {/* Score Badge */}
                  <motion.div
                    initial={{ opacity: 0, scale: 0, y: -10 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    className="absolute -top-4 left-6"
                  >
                    <motion.div
                      animate={{ x: [0, -3, 3, -3, 3, 0] }}
                      transition={{ duration: 0.4, delay: 0.2 }}
                    >
                      <Badge
                        variant="destructive"
                        className="text-sm px-4 py-1 shadow-lg"
                      >
                        Score: 32/100
                      </Badge>
                    </motion.div>
                  </motion.div>

                  <div className="mt-4">
                    {/* Prompt Text */}
                    <div className="font-mono text-lg bg-red-50 dark:bg-red-950/20 p-6 rounded-xl min-h-[80px]">
                      {displayedText}
                      {displayedText.length < BEFORE_PROMPT.length && (
                        <span
                          className={`inline-block w-0.5 h-5 bg-foreground ml-0.5 align-middle ${
                            showCursor ? "opacity-100" : "opacity-0"
                          }`}
                        />
                      )}
                    </div>

                    {/* Issues List */}
                    <div className="mt-6 space-y-2 text-sm text-muted-foreground min-h-[120px]">
                      {BEFORE_ISSUES.slice(0, visibleIssues).map((issue) => (
                        <motion.div
                          key={issue}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ duration: 0.2 }}
                          className="flex items-center gap-2"
                        >
                          <div className="h-2 w-2 rounded-full bg-red-500" />
                          {issue}
                        </motion.div>
                      ))}
                    </div>
                  </div>
                </motion.div>
              )}
            </motion.div>
          )}

          {/* After Section */}
          {isAfterPhase && (
            <motion.div
              key="after"
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              transition={{ duration: 0.4 }}
              className="space-y-6"
            >
              {/* Video */}
              {phase === "play-after-video" && (
                afterVideoSrc ? (
                  <VideoPlayer
                    src={afterVideoSrc}
                    type="after"
                    videoRef={afterVideoRef}
                    progress={videoProgress}
                  />
                ) : (
                  <VideoPlaceholder type="after" progress={videoProgress} />
                )
              )}

              {/* Prompt Card */}
              {(phase === "show-after-prompt" || phase === "complete") && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-card rounded-2xl border-2 border-green-200 dark:border-green-800 p-8 relative"
                >
                  {/* Score Badge */}
                  <motion.div
                    initial={{ opacity: 0, scale: 0, y: -10 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    transition={{ type: "spring", stiffness: 300, damping: 20 }}
                    className="absolute -top-4 left-6"
                  >
                    <Badge className="bg-green-500 hover:bg-green-500 text-white text-sm px-4 py-1 shadow-lg">
                      Score: 89/100
                    </Badge>
                  </motion.div>

                  <div className="mt-4">
                    {/* Prompt Text */}
                    <div className="font-mono text-sm bg-green-50 dark:bg-green-950/20 p-6 rounded-xl min-h-[120px] space-y-1">
                      {AFTER_PROMPT_LINES.slice(0, afterLineIndex + 1).map(
                        (line, lineIdx) => {
                          const isCurrentLine = lineIdx === afterLineIndex
                          const displayText = isCurrentLine
                            ? line.text.slice(0, afterCharIndex)
                            : line.text

                          if (!displayText && !isCurrentLine) return null

                          return (
                            <p
                              key={lineIdx}
                              className={
                                line.isHighlight
                                  ? "text-green-600 dark:text-green-400"
                                  : ""
                              }
                            >
                              {displayText}
                              {isCurrentLine && phase === "show-after-prompt" && (
                                <span
                                  className={`inline-block w-0.5 h-4 bg-foreground ml-0.5 align-middle ${
                                    showCursor ? "opacity-100" : "opacity-0"
                                  }`}
                                />
                              )}
                            </p>
                          )
                        }
                      )}
                    </div>

                    {/* Improvements List */}
                    <div className="mt-6 space-y-2 text-sm min-h-[120px]">
                      {AFTER_IMPROVEMENTS.slice(0, visibleImprovements).map(
                        (improvement) => (
                          <motion.div
                            key={improvement}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.2 }}
                            className="flex items-center gap-2 text-green-600"
                          >
                            <Check className="h-4 w-4" />
                            {improvement}
                          </motion.div>
                        )
                      )}
                    </div>
                  </div>
                </motion.div>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Replay Button */}
        <AnimatePresence>
          {phase === "complete" && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="absolute -bottom-4 right-6"
            >
              <button
                onClick={resetAnimation}
                className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors bg-background px-3 py-1.5 rounded-full border shadow-sm"
              >
                <RefreshCw className="h-3 w-3" />
                Replay
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
