import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/lib/auth"
import { Mail, Loader2, CheckCircle2, LogOut } from "lucide-react"

export function VerifyEmailPendingPage() {
  const navigate = useNavigate()
  const { user, resendVerification, logout, isEmailVerified } = useAuth()
  const [resendStatus, setResendStatus] = useState<"idle" | "loading" | "success" | "error">("idle")
  const [resendError, setResendError] = useState<string | null>(null)

  // If email is already verified, redirect to dashboard
  if (isEmailVerified) {
    navigate("/", { replace: true })
    return null
  }

  const handleResend = async () => {
    setResendStatus("loading")
    setResendError(null)
    try {
      await resendVerification()
      setResendStatus("success")
    } catch (err) {
      setResendStatus("error")
      setResendError(err instanceof Error ? err.message : "Failed to resend verification email")
    }
  }

  const handleLogout = async () => {
    await logout()
    navigate("/login", { replace: true })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 p-4 bg-primary/10 rounded-full">
            <Mail className="h-12 w-12 text-primary" />
          </div>
          <CardTitle className="text-2xl">Check your email</CardTitle>
          <CardDescription className="text-base">
            We've sent a verification link to{" "}
            <span className="font-medium text-foreground">{user?.email}</span>
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="bg-muted/50 p-4 rounded-lg text-sm text-muted-foreground space-y-2">
            <p>Click the link in the email to verify your account and access PromptLab.</p>
            <p>The link will expire in 24 hours.</p>
          </div>

          {resendStatus === "success" ? (
            <div className="flex items-center gap-2 text-green-600 justify-center p-3 bg-green-50 dark:bg-green-950/30 rounded-lg">
              <CheckCircle2 className="h-4 w-4" />
              <span className="text-sm">Verification email sent!</span>
            </div>
          ) : (
            <Button
              variant="outline"
              className="w-full"
              onClick={handleResend}
              disabled={resendStatus === "loading"}
            >
              {resendStatus === "loading" ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Sending...
                </>
              ) : (
                <>
                  <Mail className="h-4 w-4 mr-2" />
                  Resend verification email
                </>
              )}
            </Button>
          )}

          {resendStatus === "error" && resendError && (
            <p className="text-sm text-red-500 text-center">{resendError}</p>
          )}

          <div className="pt-4 border-t">
            <p className="text-sm text-muted-foreground text-center mb-3">
              Wrong email address?
            </p>
            <Button
              variant="ghost"
              className="w-full text-muted-foreground"
              onClick={handleLogout}
            >
              <LogOut className="h-4 w-4 mr-2" />
              Sign out and try again
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
