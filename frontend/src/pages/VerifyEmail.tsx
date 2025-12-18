import { useEffect, useState } from "react"
import { useSearchParams, useNavigate, Link } from "react-router-dom"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/lib/auth"
import { Loader2, CheckCircle2, XCircle, Mail } from "lucide-react"

export function VerifyEmailPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { verifyEmail, isAuthenticated, isEmailVerified } = useAuth()
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading")
  const [error, setError] = useState<string | null>(null)

  const token = searchParams.get("token")

  useEffect(() => {
    if (!token) {
      setStatus("error")
      setError("No verification token provided")
      return
    }

    const verify = async () => {
      try {
        await verifyEmail(token)
        setStatus("success")
      } catch (err) {
        setStatus("error")
        setError(err instanceof Error ? err.message : "Failed to verify email")
      }
    }

    verify()
  }, [token, verifyEmail])

  // Redirect to dashboard if already verified
  useEffect(() => {
    if (status === "success" && isAuthenticated && isEmailVerified) {
      const timer = setTimeout(() => {
        navigate("/", { replace: true })
      }, 2000)
      return () => clearTimeout(timer)
    }
  }, [status, isAuthenticated, isEmailVerified, navigate])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4">
            {status === "loading" && (
              <Loader2 className="h-12 w-12 text-primary animate-spin" />
            )}
            {status === "success" && (
              <CheckCircle2 className="h-12 w-12 text-green-500" />
            )}
            {status === "error" && (
              <XCircle className="h-12 w-12 text-red-500" />
            )}
          </div>
          <CardTitle>
            {status === "loading" && "Verifying your email..."}
            {status === "success" && "Email verified!"}
            {status === "error" && "Verification failed"}
          </CardTitle>
          <CardDescription>
            {status === "loading" && "Please wait while we verify your email address."}
            {status === "success" && "Your email has been verified. Redirecting to dashboard..."}
            {status === "error" && error}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {status === "success" && (
            <Button className="w-full" onClick={() => navigate("/", { replace: true })}>
              Go to Dashboard
            </Button>
          )}
          {status === "error" && (
            <div className="space-y-3">
              <Button className="w-full" variant="outline" asChild>
                <Link to="/login">
                  <Mail className="h-4 w-4 mr-2" />
                  Back to Login
                </Link>
              </Button>
              {isAuthenticated && !isEmailVerified && (
                <Button className="w-full" variant="outline" asChild>
                  <Link to="/verify-email-pending">
                    Resend Verification Email
                  </Link>
                </Button>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
