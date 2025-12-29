import { useState, useEffect } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"
import { useAuth } from "@/lib/auth"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardHeader, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { Mail, Lock, User, Building2, Gift } from "lucide-react"

export function LoginPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { login, register } = useAuth()
  const referralCode = searchParams.get("ref")
  const [mode, setMode] = useState<"login" | "register">(referralCode ? "register" : "login")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [name, setName] = useState("")
  const [orgName, setOrgName] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  // Auto-switch to register mode if referral code is present
  useEffect(() => {
    if (referralCode) {
      setMode("register")
    }
  }, [referralCode])

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)

    try {
      await login(email, password)
      // ProtectedRoute will redirect to verify-email-pending if not verified
      navigate("/agents")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed")
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)

    try {
      await register(email, password, name || null, orgName, referralCode || undefined)
      navigate("/agents")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/30 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 flex items-center gap-2">
            <img src="/clarynt_icon.jpg" alt="Clarynt" className="h-8 w-8" />
            <span className="text-2xl font-bold">Clarynt</span>
          </div>
          <CardDescription>
            {mode === "login" ? "Sign in to your account" : "Create a new account"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {mode === "login" ? (
            <form onSubmit={handleLogin} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="you@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="pl-9"
                    required
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="password"
                    type="password"
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="pl-9"
                    required
                  />
                </div>
              </div>
              {error && <p className="text-sm text-destructive">{error}</p>}
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? "Signing in..." : "Sign in"}
              </Button>
            </form>
          ) : (
            <form onSubmit={handleRegister} className="space-y-4">
              {referralCode && (
                <div className="flex items-center gap-2 p-3 bg-primary/10 border border-primary/20 rounded-lg text-sm">
                  <Gift className="h-5 w-5 text-primary flex-shrink-0" />
                  <span>
                    You'll get <span className="font-semibold text-primary">+25 bonus optimizations</span> as a welcome gift!
                  </span>
                </div>
              )}
              <div className="space-y-2">
                <Label htmlFor="reg-email">Email</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="reg-email"
                    type="email"
                    placeholder="you@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="pl-9"
                    required
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="reg-password">Password</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="reg-password"
                    type="password"
                    placeholder="At least 8 characters"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="pl-9"
                    minLength={8}
                    required
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="name">Your Name (optional)</Label>
                <div className="relative">
                  <User className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="name"
                    type="text"
                    placeholder="John Doe"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="pl-9"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="org-name">Organization Name</Label>
                <div className="relative">
                  <Building2 className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="org-name"
                    type="text"
                    placeholder="My Company"
                    value={orgName}
                    onChange={(e) => setOrgName(e.target.value)}
                    className="pl-9"
                    required
                  />
                </div>
              </div>
              {error && <p className="text-sm text-destructive">{error}</p>}
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? "Creating account..." : "Create Account"}
              </Button>
            </form>
          )}
        </CardContent>
        <CardFooter className="justify-center">
          <Button
            variant="link"
            onClick={() => {
              setMode(mode === "login" ? "register" : "login")
              setError("")
            }}
          >
            {mode === "login" ? "Don't have an account? Sign up" : "Already have an account? Sign in"}
          </Button>
        </CardFooter>
      </Card>
    </div>
  )
}
