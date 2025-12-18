import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from "react"
import { authApi, type User, type OrganizationBasic, type Membership } from "./api"

interface AuthState {
  user: User | null
  organization: OrganizationBasic | null
  memberships: Membership[]
  isLoading: boolean
}

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, name: string | null, organizationName: string) => Promise<void>
  logout: () => Promise<void>
  isAuthenticated: boolean
  refreshAuth: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    organization: null,
    memberships: [],
    isLoading: true,
  })

  const refreshAuth = useCallback(async () => {
    try {
      const response = await authApi.getMe()
      setState({
        user: response.user,
        organization: response.current_organization,
        memberships: response.memberships,
        isLoading: false,
      })
    } catch {
      setState({
        user: null,
        organization: null,
        memberships: [],
        isLoading: false,
      })
    }
  }, [])

  useEffect(() => {
    refreshAuth()
  }, [refreshAuth])

  const login = async (email: string, password: string) => {
    const response = await authApi.login(email, password)
    setState({
      user: response.user,
      organization: response.current_organization,
      memberships: response.memberships,
      isLoading: false,
    })
  }

  const register = async (email: string, password: string, name: string | null, organizationName: string) => {
    const response = await authApi.register(email, password, name, organizationName)
    setState({
      user: response.user,
      organization: response.current_organization,
      memberships: response.memberships,
      isLoading: false,
    })
  }

  const logout = async () => {
    await authApi.logout()
    setState({
      user: null,
      organization: null,
      memberships: [],
      isLoading: false,
    })
  }

  return (
    <AuthContext.Provider
      value={{
        ...state,
        login,
        register,
        logout,
        isAuthenticated: !!state.user,
        refreshAuth,
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
