import { cn } from "@/lib/utils"

// Shared color logic for score components
function getScoreColor(effectiveScore: number): string {
  if (effectiveScore >= 70) return "text-green-600"
  if (effectiveScore >= 50) return "text-yellow-600"
  return "text-red-600"
}

function getScoreBgColor(effectiveScore: number): string {
  if (effectiveScore >= 70) return "bg-green-50"
  if (effectiveScore >= 50) return "bg-yellow-50"
  return "bg-red-50"
}

interface ScoreGaugeProps {
  score: number
  label: string
  size?: "sm" | "md" | "lg"
  inverted?: boolean // true = lower is better (risk scores)
  showLabel?: boolean
}

export function ScoreGauge({
  score,
  label,
  size = "md",
  inverted = false,
  showLabel = true,
}: ScoreGaugeProps) {
  // Calculate display value (0-100)
  const displayScore = Math.max(0, Math.min(100, Math.round(score)))

  // For inverted (risk) scores: low = green, high = red
  // For normal scores: high = green, low = red
  const effectiveScore = inverted ? 100 - displayScore : displayScore
  const colorClass = getScoreColor(effectiveScore)

  const sizeClasses = {
    sm: "w-12 h-12 text-sm",
    md: "w-16 h-16 text-lg",
    lg: "w-20 h-20 text-xl",
  }

  const strokeWidth = size === "sm" ? 3 : size === "md" ? 4 : 5
  const radius = size === "sm" ? 20 : size === "md" ? 28 : 36
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (displayScore / 100) * circumference

  return (
    <div className="flex flex-col items-center gap-1">
      <div className={cn("relative", sizeClasses[size])}>
        {/* Background circle */}
        <svg className="w-full h-full transform -rotate-90">
          <circle
            cx="50%"
            cy="50%"
            r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth={strokeWidth}
            className="text-muted"
          />
          {/* Progress circle */}
          <circle
            cx="50%"
            cy="50%"
            r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className={cn("transition-all duration-500", colorClass)}
          />
        </svg>
        {/* Score text */}
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={cn("font-bold", colorClass)}>
            {displayScore}
          </span>
        </div>
      </div>
      {showLabel && (
        <span className="text-xs text-muted-foreground text-center max-w-[80px] leading-tight">
          {label}
        </span>
      )}
    </div>
  )
}

interface ScoreCardProps {
  score: number
  label: string
  description?: string
  inverted?: boolean
}

export function ScoreCard({ score, label, description, inverted = false }: ScoreCardProps) {
  const displayScore = Math.max(0, Math.min(100, Math.round(score)))
  const effectiveScore = inverted ? 100 - displayScore : displayScore
  const colorClass = getScoreColor(effectiveScore)
  const bgColorClass = getScoreBgColor(effectiveScore)

  return (
    <div className={cn("rounded-lg p-4", bgColorClass)}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-muted-foreground">{label}</span>
        <span className={cn("text-2xl font-bold", colorClass)}>{displayScore}</span>
      </div>
      {/* Progress bar */}
      <div className="h-2 bg-muted rounded-full overflow-hidden">
        <div
          className={cn("h-full transition-all duration-500 rounded-full", colorClass.replace("text-", "bg-"))}
          style={{ width: `${displayScore}%` }}
        />
      </div>
      {description && (
        <p className="text-xs text-muted-foreground mt-2">{description}</p>
      )}
    </div>
  )
}
