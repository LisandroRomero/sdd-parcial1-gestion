import { useState } from 'react'
import { Outlet, useNavigate } from 'react-router-dom'
import { Menu } from 'lucide-react'
import { CartBadge, CartDrawer } from '@/features/carrito'
import { useAuthStore, useUIStore } from '@/shared/lib/stores'
import { logoutUser } from '@/features/auth'
import { Sidebar } from '@/app/navigation/Sidebar'
import { Drawer } from '@/app/navigation/Drawer'
import { navigationSections } from '@/app/navigation/navigation.config'
import { useFilteredNavSections } from '@/app/navigation/navigation.hooks'

export function Layout() {
  const navigate = useNavigate()
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const user = useAuthStore((s) => s.user)
  const refreshToken = useAuthStore((s) => s.refreshToken)
  const logout = useAuthStore((s) => s.logout)
  const sidebarOpen = useUIStore((s) => s.sidebarOpen)
  const toggleSidebar = useUIStore((s) => s.toggleSidebar)

  const [drawerOpen, setDrawerOpen] = useState(false)

  const filteredSections = useFilteredNavSections(navigationSections)

  async function handleLogout() {
    try {
      if (refreshToken) {
        await logoutUser(refreshToken)
      }
    } catch {
      // Silent fail — proceed with local logout
    }
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="h-screen bg-gray-50">
      <Sidebar
        collapsed={!sidebarOpen}
        onToggle={toggleSidebar}
        sections={filteredSections}
      />
      <div
        className={`h-screen flex flex-col transition-all duration-200 ${
          sidebarOpen ? 'md:ml-64' : 'md:ml-16'
        }`}
      >
        <header className="bg-white shadow-sm flex-shrink-0">
          <div className="flex items-center justify-between px-4 h-16">
            <div className="flex items-center gap-3">
              <button
                onClick={() => setDrawerOpen(true)}
                className="md:hidden p-2 rounded-lg text-gray-500 hover:text-gray-700 hover:bg-gray-100 transition-colors"
                aria-label="Abrir navegación"
              >
                <Menu size={20} />
              </button>
            </div>
            <div className="flex items-center gap-4">
              {isAuthenticated && user && (
                <span className="text-sm text-gray-600 hidden sm:block">
                  Hola, <span className="font-medium">{user.nombre}</span>
                </span>
              )}
              {isAuthenticated && (
                <button
                  onClick={handleLogout}
                  className="text-sm text-gray-500 hover:text-gray-700 hover:bg-gray-100 px-3 py-1.5 rounded-lg transition-colors"
                >
                  Cerrar sesión
                </button>
              )}
              <CartBadge />
            </div>
          </div>
        </header>
        <main className="flex-1 overflow-auto">
          <div className="container mx-auto px-4 py-8">
            <Outlet />
          </div>
        </main>
      </div>
      <Drawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        sections={filteredSections}
      />
      <CartDrawer />
    </div>
  )
}
