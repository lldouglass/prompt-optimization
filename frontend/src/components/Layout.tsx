import { useState, useEffect } from "react"
import { Link, Outlet, useLocation } from "react-router-dom"
import { useAuth } from "@/lib/auth"
import { Button } from "@/components/ui/button"
import { LayoutDashboard, Settings, LogOut, Bot, Library, GraduationCap, BookOpen, PanelLeft, PanelLeftClose, Menu, X, Camera } from "lucide-react"
import { cn } from "@/lib/utils"

const navItems = [
  { to: "/media", icon: Camera, label: "Media Prompts" },
  { to: "/agents", icon: Bot, label: "Text Prompts" },
  { to: "/library", icon: Library, label: "Prompt Library" },
  { to: "/dashboard", icon: LayoutDashboard, label: "Requests" },
  { to: "/education", icon: GraduationCap, label: "Education" },
  { to: "/docs", icon: BookOpen, label: "Documentation" },
  { to: "/settings", icon: Settings, label: "Settings" },
]

export function Layout() {
  const { user, organization, logout } = useAuth()
  const location = useLocation()

  // Sidebar collapsed state (persisted to localStorage)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
    return localStorage.getItem('sidebar-collapsed') === 'true'
  })

  // Mobile sidebar open state
  const [mobileOpen, setMobileOpen] = useState(false)

  const toggleSidebar = () => {
    setSidebarCollapsed(prev => {
      localStorage.setItem('sidebar-collapsed', String(!prev))
      return !prev
    })
  }

  // Close mobile sidebar on route change
  useEffect(() => {
    setMobileOpen(false)
  }, [location.pathname])

  // Close mobile sidebar on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setMobileOpen(false)
    }
    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [])

  const SidebarContent = ({ isMobile = false }: { isMobile?: boolean }) => (
    <>
      {/* Header */}
      <div className={cn(
        "border-b flex items-center",
        sidebarCollapsed && !isMobile ? "p-2 justify-center" : "p-4 justify-between"
      )}>
        <Link
          to="/dashboard"
          className={cn(
            "flex items-center gap-2 font-semibold text-lg",
            sidebarCollapsed && !isMobile && "justify-center"
          )}
        >
          <img src="/clarynt_icon.jpg" alt="Clarynt" className="h-6 w-6" />
          {(!sidebarCollapsed || isMobile) && "Clarynt"}
        </Link>

        {/* Desktop toggle button */}
        {!isMobile && (
          <Button
            variant="ghost"
            size="icon"
            className={cn(
              "h-8 w-8 shrink-0",
              sidebarCollapsed && "absolute right-0 translate-x-1/2 bg-card border shadow-sm"
            )}
            onClick={toggleSidebar}
            title={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {sidebarCollapsed ? (
              <PanelLeft className="h-4 w-4" />
            ) : (
              <PanelLeftClose className="h-4 w-4" />
            )}
          </Button>
        )}

        {/* Mobile close button */}
        {isMobile && (
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={() => setMobileOpen(false)}
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>

      {/* Navigation */}
      <nav className={cn(
        "flex-1 space-y-1",
        sidebarCollapsed && !isMobile ? "p-2" : "p-4"
      )}>
        {navItems.map(({ to, icon: Icon, label }) => (
          <Link
            key={to}
            to={to}
            title={sidebarCollapsed && !isMobile ? label : undefined}
            className={cn(
              "flex items-center rounded-md text-sm font-medium transition-colors",
              sidebarCollapsed && !isMobile
                ? "justify-center p-2"
                : "gap-3 px-3 py-2",
              location.pathname === to
                ? "bg-secondary text-secondary-foreground"
                : "text-muted-foreground hover:bg-secondary/50 hover:text-foreground"
            )}
          >
            <Icon className="h-4 w-4 shrink-0" />
            {(!sidebarCollapsed || isMobile) && label}
          </Link>
        ))}
      </nav>

      {/* User Profile */}
      <div className={cn(
        "border-t",
        sidebarCollapsed && !isMobile ? "p-2" : "p-4"
      )}>
        <div className={cn(
          "flex items-center mb-3",
          sidebarCollapsed && !isMobile ? "justify-center" : "gap-3"
        )}>
          {user?.avatar_url ? (
            <img
              src={user.avatar_url}
              alt={user.name || user.email}
              className="h-8 w-8 rounded-full shrink-0"
              title={sidebarCollapsed && !isMobile ? user.name || user.email : undefined}
            />
          ) : (
            <div
              className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-sm font-medium text-primary shrink-0"
              title={sidebarCollapsed && !isMobile ? user?.name || user?.email : undefined}
            >
              {(user?.name || user?.email || "?")[0].toUpperCase()}
            </div>
          )}
          {(!sidebarCollapsed || isMobile) && (
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium truncate">
                {user?.name || user?.email}
              </div>
              <div className="text-xs text-muted-foreground truncate">
                {organization?.name}
              </div>
            </div>
          )}
        </div>
        <Button
          variant="ghost"
          size="sm"
          className={cn(
            sidebarCollapsed && !isMobile ? "w-full justify-center p-2" : "w-full justify-start"
          )}
          onClick={logout}
          title={sidebarCollapsed && !isMobile ? "Sign out" : undefined}
        >
          <LogOut className={cn("h-4 w-4", (!sidebarCollapsed || isMobile) && "mr-2")} />
          {(!sidebarCollapsed || isMobile) && "Sign out"}
        </Button>
      </div>
    </>
  )

  return (
    <div className="flex h-screen bg-background">
      {/* Mobile sidebar overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 md:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Mobile sidebar */}
      <aside className={cn(
        "fixed inset-y-0 left-0 z-50 w-64 bg-card flex flex-col transform transition-transform duration-300 ease-in-out md:hidden",
        mobileOpen ? "translate-x-0" : "-translate-x-full"
      )}>
        <SidebarContent isMobile />
      </aside>

      {/* Desktop sidebar */}
      <aside className={cn(
        "hidden md:flex flex-col border-r bg-card transition-all duration-300 relative",
        sidebarCollapsed ? "w-16" : "w-64"
      )}>
        <SidebarContent />
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Mobile header with menu button */}
        <header className="md:hidden flex items-center gap-3 p-4 border-b bg-card">
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={() => setMobileOpen(true)}
          >
            <Menu className="h-5 w-5" />
          </Button>
          <Link to="/dashboard" className="flex items-center gap-2 font-semibold">
            <img src="/clarynt_icon.jpg" alt="Clarynt" className="h-5 w-5" />
            Clarynt
          </Link>
        </header>

        <main className="flex-1 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
