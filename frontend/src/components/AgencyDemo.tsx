import { useState, useEffect, useRef, useCallback } from "react"
import { motion, AnimatePresence } from "motion/react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Check, X, Play, Pause, ChevronLeft, ChevronRight, HelpCircle, AlertTriangle } from "lucide-react"
import {
  beforeImages,
  afterImages,
  originalPrompt,
  optimizedPrompt,
  clarifyingQuestions,
  checklist,
  matchScore,
  productBrief,
  inconsistencyCallouts,
} from "@/config/demo"

type Phase = "before" | "questions" | "after"
type ViewMode = "animation" | "before" | "after"

// Check reduced motion preference outside component (runs once on module load)
const getReducedMotionPreference = () => {
  if (typeof window === "undefined") return false
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches
}

// Placeholder component for missing images
function ImagePlaceholder({ index, type }: { index: number; type: "before" | "after" }) {
  return (
    <div className="aspect-square bg-muted rounded-lg flex items-center justify-center border-2 border-dashed border-muted-foreground/30">
      <div className="text-center text-muted-foreground text-sm p-4">
        <div className="mb-2">
          {type === "before" ? "Before" : "After"} #{index + 1}
        </div>
        <div className="text-xs opacity-60">
          Add image to<br />
          public/demo/{type}/
        </div>
      </div>
    </div>
  )
}

// Image grid component
function ImageGrid({
  images,
  type,
  isVisible,
  showCallouts = false,
  visibleCallouts = 0,
}: {
  images: string[]
  type: "before" | "after"
  isVisible: boolean
  showCallouts?: boolean
  visibleCallouts?: number
}) {
  // Always render 4 slots
  const slots = [0, 1, 2, 3]

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: isVisible ? 1 : 0.3 }}
      transition={{ duration: 0.5 }}
      className="grid grid-cols-2 gap-3"
    >
      {slots.map((index) => {
        const imageSrc = images[index]
        const callout = type === "before" ? inconsistencyCallouts[index] : null
        const showThisCallout = showCallouts && index < visibleCallouts

        return (
          <motion.div
            key={index}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4, delay: index * 0.15 }}
            className="relative"
          >
            {imageSrc ? (
              <>
                <img
                  src={`/demo/${type}/${imageSrc}`}
                  alt={`${type} result ${index + 1}`}
                  className={`aspect-square object-cover rounded-lg border shadow-sm transition-all duration-300 ${
                    type === "before" && showCallouts ? "border-red-400 border-2" : ""
                  }`}
                />
                {/* Inconsistency callout overlay */}
                <AnimatePresence>
                  {showThisCallout && callout && (
                    <motion.div
                      initial={{ opacity: 0, y: 10, scale: 0.9 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.9 }}
                      transition={{ duration: 0.3 }}
                      className="absolute bottom-2 left-2 right-2"
                    >
                      <div className="bg-red-500/90 text-white text-xs px-2 py-1.5 rounded-md flex items-center gap-1.5 shadow-lg">
                        <AlertTriangle className="h-3 w-3 flex-shrink-0" />
                        <span className="font-medium">{callout}</span>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </>
            ) : (
              <ImagePlaceholder index={index} type={type} />
            )}
          </motion.div>
        )
      })}
    </motion.div>
  )
}

// Animated score counter
function AnimatedScore({
  from,
  to,
  duration = 1000,
}: {
  from: number
  to: number
  duration?: number
}) {
  const [current, setCurrent] = useState(from)

  useEffect(() => {
    const startTime = Date.now()
    const animate = () => {
      const elapsed = Date.now() - startTime
      const progress = Math.min(elapsed / duration, 1)
      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3)
      setCurrent(Math.round(from + (to - from) * eased))
      if (progress < 1) {
        requestAnimationFrame(animate)
      }
    }
    requestAnimationFrame(animate)
  }, [from, to, duration])

  return <span>{current}</span>
}

// Main demo component
export function AgencyDemo() {
  // Check reduced motion preference using state (initialized from helper)
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(getReducedMotionPreference)
  const [phase, setPhase] = useState<Phase>("before")
  const [viewMode, setViewMode] = useState<ViewMode>(() =>
    getReducedMotionPreference() ? "before" : "animation"
  )
  const [isPlaying, setIsPlaying] = useState(false)
  const [hasInteracted, setHasInteracted] = useState(false)
  const [visibleQuestions, setVisibleQuestions] = useState(0)
  const [visibleChecklist, setVisibleChecklist] = useState(0)
  const [visibleCallouts, setVisibleCallouts] = useState(0)
  const [showScore, setShowScore] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  // Listen for reduced motion preference changes
  useEffect(() => {
    if (typeof window === "undefined") return
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)")
    const handler = (e: MediaQueryListEvent) => {
      setPrefersReducedMotion(e.matches)
      if (e.matches) {
        setViewMode("before")
        setIsPlaying(false)
      }
    }
    mediaQuery.addEventListener("change", handler)
    return () => mediaQuery.removeEventListener("change", handler)
  }, [])

  // Intersection observer to start animation when visible
  useEffect(() => {
    if (prefersReducedMotion) return

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !hasInteracted) {
            setIsPlaying(true)
          } else if (!entry.isIntersecting) {
            setIsPlaying(false)
          }
        })
      },
      { threshold: 0.3 }
    )

    if (containerRef.current) {
      observer.observe(containerRef.current)
    }

    return () => observer.disconnect()
  }, [hasInteracted, prefersReducedMotion])

  // Clear any pending timers
  const clearTimers = useCallback(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current)
      timerRef.current = null
    }
  }, [])

  // Phase transition logic
  useEffect(() => {
    if (!isPlaying || viewMode !== "animation") {
      clearTimers()
      return
    }

    clearTimers()

    if (phase === "before") {
      // First, animate the callouts appearing one by one
      if (visibleCallouts < inconsistencyCallouts.length) {
        timerRef.current = setTimeout(() => {
          setVisibleCallouts((prev) => prev + 1)
        }, 800) // 800ms between each callout
      } else {
        // All callouts shown, wait 2s then transition to questions
        timerRef.current = setTimeout(() => {
          setPhase("questions")
          setVisibleQuestions(0)
          setVisibleCallouts(0)
        }, 2000)
      }
    } else if (phase === "questions") {
      // Animate questions appearing one by one (slower)
      if (visibleQuestions < clarifyingQuestions.length) {
        timerRef.current = setTimeout(() => {
          setVisibleQuestions((prev) => prev + 1)
        }, 700) // 700ms between each question
      } else {
        // All questions shown, wait then transition to after
        timerRef.current = setTimeout(() => {
          setPhase("after")
          setVisibleChecklist(0)
          setShowScore(false)
        }, 2000)
      }
    } else if (phase === "after") {
      // Animate checklist and score
      if (!showScore) {
        timerRef.current = setTimeout(() => {
          setShowScore(true)
        }, 600)
      } else if (visibleChecklist < checklist.length) {
        timerRef.current = setTimeout(() => {
          setVisibleChecklist((prev) => prev + 1)
        }, 250) // Slightly slower checklist reveal
      } else {
        // Complete, wait longer then loop back
        timerRef.current = setTimeout(() => {
          setPhase("before")
          setVisibleQuestions(0)
          setVisibleChecklist(0)
          setVisibleCallouts(0)
          setShowScore(false)
        }, 5000) // 5s to view final result
      }
    }

    return clearTimers
  }, [isPlaying, viewMode, phase, visibleQuestions, visibleChecklist, visibleCallouts, showScore, clearTimers])

  // Handle user interaction
  const handleUserInteraction = () => {
    setHasInteracted(true)
  }

  const togglePlayPause = () => {
    handleUserInteraction()
    setIsPlaying(!isPlaying)
    if (!isPlaying) {
      setViewMode("animation")
    }
  }

  const showBefore = () => {
    handleUserInteraction()
    setIsPlaying(false)
    setViewMode("before")
    setPhase("before")
  }

  const showAfter = () => {
    handleUserInteraction()
    setIsPlaying(false)
    setViewMode("after")
    setPhase("after")
    setShowScore(true)
    setVisibleChecklist(checklist.length)
  }

  // Parse match score for animation
  const scoreNum = parseInt(matchScore.split("/")[0])
  const scoreTotal = parseInt(matchScore.split("/")[1])

  // For reduced motion: show static side-by-side
  if (prefersReducedMotion && viewMode !== "animation") {
    return (
      <div ref={containerRef} className="space-y-6">
        {/* Controls */}
        <div className="flex justify-center gap-2">
          <Button
            variant={viewMode === "before" ? "default" : "outline"}
            size="sm"
            onClick={showBefore}
          >
            <ChevronLeft className="h-4 w-4 mr-1" />
            Show Before
          </Button>
          <Button
            variant={viewMode === "after" ? "default" : "outline"}
            size="sm"
            onClick={showAfter}
          >
            Show After
            <ChevronRight className="h-4 w-4 ml-1" />
          </Button>
        </div>

        {/* Static comparison */}
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Before side */}
          <Card className={viewMode === "before" ? "ring-2 ring-primary" : "opacity-50"}>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <span className="text-red-500">Before</span>
                <Badge variant="outline" className="text-red-500 border-red-500">
                  Model guessing
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-muted/50 p-4 rounded-lg font-mono text-sm">
                {originalPrompt}
              </div>
              <ImageGrid images={beforeImages} type="before" isVisible={true} />
            </CardContent>
          </Card>

          {/* After side */}
          <Card className={viewMode === "after" ? "ring-2 ring-primary" : "opacity-50"}>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <span className="text-green-500">After</span>
                <Badge className="bg-green-500 hover:bg-green-500 text-white">
                  Match: {matchScore}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-muted/50 p-4 rounded-lg font-mono text-sm">
                {optimizedPrompt}
              </div>
              <ImageGrid images={afterImages} type="after" isVisible={true} />
              <div className="grid grid-cols-2 gap-2 text-sm">
                {checklist.map((item) => (
                  <div
                    key={item.label}
                    className={`flex items-center gap-2 ${
                      item.met ? "text-green-600" : "text-red-500"
                    }`}
                  >
                    {item.met ? (
                      <Check className="h-4 w-4 flex-shrink-0" />
                    ) : (
                      <X className="h-4 w-4 flex-shrink-0" />
                    )}
                    <span className="truncate">{item.label}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div ref={containerRef} className="space-y-6">
      {/* Controls */}
      <div className="flex justify-center gap-2 flex-wrap">
        <Button variant="outline" size="sm" onClick={togglePlayPause}>
          {isPlaying ? (
            <>
              <Pause className="h-4 w-4 mr-1" />
              Pause
            </>
          ) : (
            <>
              <Play className="h-4 w-4 mr-1" />
              Play
            </>
          )}
        </Button>
        <Button
          variant={viewMode === "before" ? "default" : "outline"}
          size="sm"
          onClick={showBefore}
        >
          <ChevronLeft className="h-4 w-4 mr-1" />
          Show Before
        </Button>
        <Button
          variant={viewMode === "after" ? "default" : "outline"}
          size="sm"
          onClick={showAfter}
        >
          Show After
          <ChevronRight className="h-4 w-4 ml-1" />
        </Button>
      </div>

      {/* Main demo area */}
      <div className="grid lg:grid-cols-2 gap-8">
        {/* Left side: Product brief + Prompt */}
        <div className="space-y-6">
          {/* Product Brief Card */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base font-medium">What we asked for</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <div className="text-sm text-muted-foreground mb-1">Product</div>
                <div className="font-medium">{productBrief.product}</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground mb-1">Must-haves</div>
                <div className="flex flex-wrap gap-2">
                  {productBrief.mustHaves.map((item) => (
                    <Badge key={item} variant="secondary" className="text-xs">
                      {item}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Prompt display */}
          <AnimatePresence mode="wait">
            {(phase === "before" || viewMode === "before") && (
              <motion.div
                key="original-prompt"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.3 }}
              >
                <Card className="border-red-200 dark:border-red-800">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base font-medium flex items-center gap-2">
                      Original prompt
                      <Badge variant="outline" className="text-red-500 border-red-500 text-xs">
                        Model is guessing
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="bg-red-50 dark:bg-red-950/20 p-4 rounded-lg font-mono text-sm">
                      {originalPrompt}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )}

            {phase === "questions" && viewMode === "animation" && (
              <motion.div
                key="questions"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.3 }}
              >
                <Card className="border-primary">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base font-medium flex items-center gap-2">
                      <HelpCircle className="h-4 w-4 text-primary" />
                      Clayrnt asks clarifying questions
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {clarifyingQuestions.slice(0, visibleQuestions).map((q, i) => (
                        <motion.div
                          key={i}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ duration: 0.3 }}
                          className="flex items-start gap-3 text-sm"
                        >
                          <span className="flex-shrink-0 h-5 w-5 rounded-full bg-primary/10 text-primary text-xs flex items-center justify-center font-medium">
                            {i + 1}
                          </span>
                          <span>{q}</span>
                        </motion.div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )}

            {(phase === "after" || viewMode === "after") && (
              <motion.div
                key="optimized-prompt"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.3 }}
              >
                <Card className="border-green-200 dark:border-green-800">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base font-medium flex items-center gap-2">
                      Optimized prompt
                      <span className="text-xs text-muted-foreground font-normal">
                        (from Clayrnt)
                      </span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="bg-green-50 dark:bg-green-950/20 p-4 rounded-lg font-mono text-sm max-h-48 overflow-y-auto">
                      {optimizedPrompt}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Match Score and Checklist */}
          <AnimatePresence>
            {((phase === "after" && showScore) || viewMode === "after") && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 20 }}
                transition={{ duration: 0.4 }}
              >
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base font-medium flex items-center justify-between">
                      <span>Match Score</span>
                      <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ type: "spring", stiffness: 300, damping: 20 }}
                      >
                        <Badge className="bg-green-500 hover:bg-green-500 text-white text-lg px-3 py-1">
                          {viewMode === "animation" ? (
                            <>
                              <AnimatedScore from={3} to={scoreNum} duration={800} />/
                              {scoreTotal}
                            </>
                          ) : (
                            matchScore
                          )}
                        </Badge>
                      </motion.div>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
                      {checklist
                        .slice(0, viewMode === "after" ? checklist.length : visibleChecklist)
                        .map((item, i) => (
                          <motion.div
                            key={item.label}
                            initial={viewMode === "animation" ? { opacity: 0, x: -10 } : false}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.2 }}
                            className={`flex items-center gap-2 ${
                              item.met
                                ? "text-green-600 dark:text-green-400"
                                : "text-red-500 dark:text-red-400"
                            }`}
                          >
                            {item.met ? (
                              <motion.div
                                initial={
                                  viewMode === "animation" ? { scale: 0, rotate: -180 } : false
                                }
                                animate={{ scale: 1, rotate: 0 }}
                                transition={{
                                  type: "spring",
                                  stiffness: 400,
                                  damping: 15,
                                  delay: i * 0.05,
                                }}
                              >
                                <Check className="h-4 w-4 flex-shrink-0" />
                              </motion.div>
                            ) : (
                              <X className="h-4 w-4 flex-shrink-0" />
                            )}
                            <span className="truncate">{item.label}</span>
                          </motion.div>
                        ))}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Right side: Image grid */}
        <div className="space-y-4">
          <AnimatePresence mode="wait">
            {(phase === "before" || viewMode === "before") && (
              <motion.div
                key="before-images"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.5 }}
              >
                <div className="text-sm text-red-500 font-medium mb-3 text-center flex items-center justify-center gap-2">
                  <AlertTriangle className="h-4 w-4" />
                  Inconsistent results without Clayrnt
                </div>
                <ImageGrid
                  images={beforeImages}
                  type="before"
                  isVisible={true}
                  showCallouts={phase === "before" && viewMode === "animation"}
                  visibleCallouts={visibleCallouts}
                />
              </motion.div>
            )}

            {phase === "questions" && viewMode === "animation" && (
              <motion.div
                key="questions-images"
                initial={{ opacity: 1 }}
                animate={{ opacity: 0.3 }}
                transition={{ duration: 0.5 }}
              >
                <div className="text-sm text-muted-foreground mb-3 text-center">
                  Inconsistent results without Clayrnt
                </div>
                <ImageGrid images={beforeImages} type="before" isVisible={false} />
              </motion.div>
            )}

            {(phase === "after" || viewMode === "after") && (
              <motion.div
                key="after-images"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.5 }}
              >
                <div className="text-sm text-green-600 font-medium mb-3 text-center flex items-center justify-center gap-2">
                  <Check className="h-4 w-4" />
                  Consistent results with Clayrnt
                </div>
                <ImageGrid images={afterImages} type="after" isVisible={true} />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}
