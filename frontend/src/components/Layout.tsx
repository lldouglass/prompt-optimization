import { Link, Outlet, useLocation } from "react-router-dom"
import { useAuth } from "@/lib/auth"
import { Button } from "@/components/ui/button"
import { LayoutDashboard, Settings, LogOut, Bot, Library, GraduationCap, BookOpen } from "lucide-react"
import { cn } from "@/lib/utils"

const navItems = [
  { to: "/agents", icon: Bot, label: "Agents" },
  { to: "/library", icon: Library, label: "Prompt Library" },
  { to: "/dashboard", icon: LayoutDashboard, label: "Requests" },
  { to: "/education", icon: GraduationCap, label: "Education" },
  { to: "/docs", icon: BookOpen, label: "Documentation" },
  { to: "/settings", icon: Settings, label: "Settings" },
]

export function Layout() {
  const { user, organization, logout } = useAuth()
  const location = useLocation()

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <aside className="w-64 border-r bg-card flex flex-col">
        <div className="p-4 border-b">
          <Link to="/dashboard" className="flex items-center gap-2 font-semibold text-lg">
            <img src="/clarynt_icon.jpg" alt="Clarynt" className="h-6 w-6" />
            Clarynt
          </Link>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {navItems.map(({ to, icon: Icon, label }) => (
            <Link
              key={to}
              to={to}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                location.pathname === to
                  ? "bg-secondary text-secondary-foreground"
                  : "text-muted-foreground hover:bg-secondary/50 hover:text-foreground"
              )}
            >
              <Icon className="h-4 w-4" />
              {label}
            </Link>
          ))}
        </nav>

        <div className="p-4 border-t">
          <div className="flex items-center gap-3 mb-3">
            {user?.avatar_url ? (
              <img
                src={user.avatar_url}
                alt={user.name || user.email}
                className="h-8 w-8 rounded-full"
              />
            ) : (
              <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-sm font-medium text-primary">
                {(user?.name || user?.email || "?")[0].toUpperCase()}
              </div>
            )}
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium truncate">
                {user?.name || user?.email}
              </div>
              <div className="text-xs text-muted-foreground truncate">
                {organization?.name}
              </div>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="w-full justify-start"
            onClick={logout}
          >
            <LogOut className="h-4 w-4 mr-2" />
            Sign out
          </Button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  )
}
