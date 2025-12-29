import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "motion/react"
import { Badge } from "@/components/ui/badge"
import { Check, RefreshCw } from "lucide-react"

const BEFORE_PROMPT = "Write a summary of the article. Make it good and include the important parts."

const AFTER_PROMPT_LINES = [
  { text: "<role>", isTag: true },
  { text: "You are an expert content analyst specializing in extracting key insights.", isTag: false },
  { text: "</role>", isTag: true },
  { text: "", isTag: false },
  { text: "<task>", isTag: true },
  { text: "Create a concise summary that:", isTag: false },
  { text: "- Captures the main thesis in 1-2 sentences", isTag: false },
  { text: "- Lists 3-5 key supporting points", isTag: false },
  { text: "- Keeps total length under 150 words", isTag: false },
  { text: "</task>", isTag: true },
]

const BEFORE_ISSUES = [
  "No role definition",
  "Vague instructions",
  "Missing output format",
  "No examples provided",
]

const AFTER_IMPROVEMENTS = [
  "Expert role defined",
  "Clear, specific instructions",
  "Structured XML format",
  "+57 point improvement",
]

type Phase = "typing-before" | "show-before-score" | "transforming" | "typing-after" | "show-after-score" | "complete"

export function AnimatedDemo() {
  const [phase, setPhase] = useState<Phase>("typing-before")
  const [displayedText, setDisplayedText] = useState("")
  const [afterLineIndex, setAfterLineIndex] = useState(0)
  const [afterCharIndex, setAfterCharIndex] = useState(0)
  const [visibleIssues, setVisibleIssues] = useState(0)
  const [visibleImprovements, setVisibleImprovements] = useState(0)
  const [showCursor, setShowCursor] = useState(true)

  // Cursor blink effect
  useEffect(() => {
    const interval = setInterval(() => {
      setShowCursor(prev => !prev)
    }, 530)
    return () => clearInterval(interval)
  }, [])

  // Phase 1: Type out the "before" prompt
  useEffect(() => {
    if (phase !== "typing-before") return

    if (displayedText.length < BEFORE_PROMPT.length) {
      const timeout = setTimeout(() => {
        setDisplayedText(BEFORE_PROMPT.slice(0, displayedText.length + 1))
      }, 40)
      return () => clearTimeout(timeout)
    } else {
      // Done typing, show score after a pause
      const timeout = setTimeout(() => setPhase("show-before-score"), 500)
      return () => clearTimeout(timeout)
    }
  }, [phase, displayedText])

  // Phase 2: Show before score and issues
  useEffect(() => {
    if (phase !== "show-before-score") return

    if (visibleIssues < BEFORE_ISSUES.length) {
      const timeout = setTimeout(() => {
        setVisibleIssues(prev => prev + 1)
      }, 300)
      return () => clearTimeout(timeout)
    } else {
      // All issues shown, start transformation after pause
      const timeout = setTimeout(() => setPhase("transforming"), 1500)
      return () => clearTimeout(timeout)
    }
  }, [phase, visibleIssues])

  // Phase 3: Transforming (brief pause for visual effect)
  useEffect(() => {
    if (phase !== "transforming") return
    const timeout = setTimeout(() => {
      setPhase("typing-after")
    }, 800)
    return () => clearTimeout(timeout)
  }, [phase])

  // Phase 4: Type out the "after" prompt line by line
  useEffect(() => {
    if (phase !== "typing-after") return

    if (afterLineIndex < AFTER_PROMPT_LINES.length) {
      const currentLine = AFTER_PROMPT_LINES[afterLineIndex].text

      if (afterCharIndex < currentLine.length) {
        const timeout = setTimeout(() => {
          setAfterCharIndex(prev => prev + 1)
        }, AFTER_PROMPT_LINES[afterLineIndex].isTag ? 25 : 20)
        return () => clearTimeout(timeout)
      } else {
        // Move to next line
        const timeout = setTimeout(() => {
          setAfterLineIndex(prev => prev + 1)
          setAfterCharIndex(0)
        }, 100)
        return () => clearTimeout(timeout)
      }
    } else {
      // Done typing after, show score
      const timeout = setTimeout(() => setPhase("show-after-score"), 400)
      return () => clearTimeout(timeout)
    }
  }, [phase, afterLineIndex, afterCharIndex])

  // Phase 5: Show after score and improvements
  useEffect(() => {
    if (phase !== "show-after-score") return

    if (visibleImprovements < AFTER_IMPROVEMENTS.length) {
      const timeout = setTimeout(() => {
        setVisibleImprovements(prev => prev + 1)
      }, 300)
      return () => clearTimeout(timeout)
    } else {
      const timeout = setTimeout(() => setPhase("complete"), 1000)
      return () => clearTimeout(timeout)
    }
  }, [phase, visibleImprovements])

  const resetAnimation = () => {
    setPhase("typing-before")
    setDisplayedText("")
    setAfterLineIndex(0)
    setAfterCharIndex(0)
    setVisibleIssues(0)
    setVisibleImprovements(0)
  }

  const isBeforePhase = phase === "typing-before" || phase === "show-before-score"
  const isTransforming = phase === "transforming"
  const isAfterPhase = phase === "typing-after" || phase === "show-after-score" || phase === "complete"

  return (
    <div className="max-w-3xl mx-auto">
      <div className="relative">
        <AnimatePresence mode="wait">
          {/* Before Card */}
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
              className="bg-card rounded-2xl border-2 border-red-200 dark:border-red-800 p-8 relative"
            >
              {/* Score Badge */}
              <AnimatePresence>
                {phase === "show-before-score" && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0, y: -10 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    className="absolute -top-4 left-6"
                  >
                    <motion.div
                      animate={{ x: [0, -3, 3, -3, 3, 0] }}
                      transition={{ duration: 0.4, delay: 0.2 }}
                    >
                      <Badge variant="destructive" className="text-sm px-4 py-1 shadow-lg">
                        Score: 32/100
                      </Badge>
                    </motion.div>
                  </motion.div>
                )}
              </AnimatePresence>

              <div className="mt-4">
                {/* Prompt Text */}
                <div className="font-mono text-lg bg-red-50 dark:bg-red-950/20 p-6 rounded-xl min-h-[100px]">
                  {displayedText}
                  {phase === "typing-before" && (
                    <span className={`inline-block w-0.5 h-5 bg-foreground ml-0.5 align-middle ${showCursor ? 'opacity-100' : 'opacity-0'}`} />
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

          {/* After Card */}
          {isAfterPhase && (
            <motion.div
              key="after"
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              transition={{ duration: 0.4 }}
              className="bg-card rounded-2xl border-2 border-green-200 dark:border-green-800 p-8 relative"
            >
              {/* Score Badge */}
              <AnimatePresence>
                {(phase === "show-after-score" || phase === "complete") && (
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
                )}
              </AnimatePresence>

              <div className="mt-4">
                {/* Prompt Text */}
                <div className="font-mono text-sm bg-green-50 dark:bg-green-950/20 p-6 rounded-xl min-h-[200px] space-y-1">
                  {AFTER_PROMPT_LINES.slice(0, afterLineIndex + 1).map((line, lineIdx) => {
                    const isCurrentLine = lineIdx === afterLineIndex
                    const displayText = isCurrentLine
                      ? line.text.slice(0, afterCharIndex)
                      : line.text

                    if (!displayText && !isCurrentLine) return null

                    return (
                      <p key={lineIdx} className={line.isTag ? "text-green-600 dark:text-green-400" : ""}>
                        {displayText}
                        {isCurrentLine && phase === "typing-after" && (
                          <span className={`inline-block w-0.5 h-4 bg-foreground ml-0.5 align-middle ${showCursor ? 'opacity-100' : 'opacity-0'}`} />
                        )}
                      </p>
                    )
                  })}
                </div>

                {/* Improvements List */}
                <div className="mt-6 space-y-2 text-sm min-h-[120px]">
                  {AFTER_IMPROVEMENTS.slice(0, visibleImprovements).map((improvement) => (
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
                  ))}
                </div>
              </div>
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
