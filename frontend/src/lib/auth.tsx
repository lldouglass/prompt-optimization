import { createContext, useContext, useState, useEffect, type ReactNode } from "react"
import type { Organization, ApiKey } from "./api"

interface AuthState {
  organization: Organization | null
  apiKey: ApiKey | null
  rawApiKey: string | null
}

interface AuthContextType extends AuthState {
  login: (org: Organization, apiKey: ApiKey, rawKey: string) => void
  logout: () => void
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | null>(null)

const STORAGE_KEY = "promptlab_auth"

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>(() => {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      try {
        return JSON.parse(stored)
      } catch {
        return { organization: null, apiKey: null, rawApiKey: null }
      }
    }
    return { organization: null, apiKey: null, rawApiKey: null }
  })

  useEffect(() => {
    if (state.organization && state.apiKey && state.rawApiKey) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
    } else {
      localStorage.removeItem(STORAGE_KEY)
    }
  }, [state])

  const login = (org: Organization, apiKey: ApiKey, rawKey: string) => {
    setState({ organization: org, apiKey, rawApiKey: rawKey })
  }

  const logout = () => {
    setState({ organization: null, apiKey: null, rawApiKey: null })
  }

  return (
    <AuthContext.Provider
      value={{
        ...state,
        login,
        logout,
        isAuthenticated: !!state.rawApiKey,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error("useAuth must be used within AuthProvider")
  return ctx
}
