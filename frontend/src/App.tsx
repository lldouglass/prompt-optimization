import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import { AuthProvider, useAuth } from "@/lib/auth"
import { Layout } from "@/components/Layout"
import { LandingPageV2 } from "@/pages/LandingV2"
import { LoginPage } from "@/pages/Login"
import { DashboardPage } from "@/pages/Dashboard"
import { SettingsPage } from "@/pages/Settings"
import { AgentsPage } from "@/pages/Agents"
import { MediaOptimizerPage } from "@/pages/MediaOptimizer"
import { PromptLibraryPage } from "@/pages/PromptLibrary"
import { VerifyEmailPage } from "@/pages/VerifyEmail"
import { VerifyEmailPendingPage } from "@/pages/VerifyEmailPending"
import { EducationPage } from "@/pages/Education"
import { DocumentationPage } from "@/pages/Documentation"

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (isAuthenticated) {
    return <Navigate to="/media" replace />
  }
  return <>{children}</>
}

function AppRoutes() {
  return (
    <Routes>
      {/* Public landing page - always accessible */}
      <Route path="/" element={<LandingPageV2 />} />
      {/* Landing page also at /home for logged-in users */}
      <Route path="/home" element={<LandingPageV2 />} />
      <Route
        path="/login"
        element={
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        }
      />
      {/* Email verification routes */}
      <Route path="/verify-email" element={<VerifyEmailPage />} />
      <Route path="/verify-email-pending" element={<VerifyEmailPendingPage />} />
      {/* Public pages with navigation layout */}
      <Route element={<Layout />}>
        <Route path="/education" element={<EducationPage />} />
        <Route path="/docs" element={<DocumentationPage />} />
      </Route>
      {/* Protected app routes (require authentication AND email verification) */}
      <Route
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route path="/media" element={<MediaOptimizerPage />} />
        <Route path="/agents" element={<AgentsPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/library" element={<PromptLibraryPage />} />
      </Route>
    </Routes>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  )
}
