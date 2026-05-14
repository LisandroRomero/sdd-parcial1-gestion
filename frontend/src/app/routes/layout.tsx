import { Outlet, useNavigate, NavLink } from 'react-router-dom'
import { CartBadge, CartDrawer } from '@/features/carrito'
import { useAuthStore } from '@/shared/lib/stores'
import { logoutUser } from '@/features/auth'

export function Layout() {
  const navigate = useNavigate()
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const user = useAuthStore((s) => s.user)
  const refreshToken = useAuthStore((s) => s.refreshToken)
  const logout = useAuthStore((s) => s.logout)

  async function handleLogout() {
    try {
      if (refreshToken) {
        await logoutUser(refreshToken)
      }
    } catch {
      // Silent fail — proceed with local logout regardless
    }
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <h1 className="text-xl font-bold text-gray-900">Food Store</h1>
            <nav className="flex items-center gap-4">
              <NavLink
                to="/catalogo"
                end={false}
                className={({ isActive }) =>
                  isActive
                    ? 'text-orange-500 font-semibold text-sm'
                    : 'text-gray-600 hover:text-gray-900 text-sm transition-colors'
                }
              >
                Catálogo
              </NavLink>
              <NavLink
                to="/pedidos"
                end={false}
                className={({ isActive }) =>
                  isActive
                    ? 'text-orange-500 font-semibold text-sm'
                    : 'text-gray-600 hover:text-gray-900 text-sm transition-colors'
                }
              >
                {user?.roles.includes('CLIENT') ? 'Mis Pedidos' : 'Pedidos'}
              </NavLink>
              <NavLink
                to="/perfil"
                end={false}
                className={({ isActive }) =>
                  isActive
                    ? 'text-orange-500 font-semibold text-sm'
                    : 'text-gray-600 hover:text-gray-900 text-sm transition-colors'
                }
              >
                Mi Perfil
              </NavLink>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            {isAuthenticated && user && (
              <div className="flex items-center gap-3">
                <span className="text-sm text-gray-600">
                  Hola, <span className="font-medium text-gray-900">{user.nombre}</span>
                </span>
                <button
                  onClick={handleLogout}
                  className="text-sm text-gray-500 hover:text-gray-700 hover:bg-gray-100 px-3 py-1.5 rounded-lg transition-colors"
                >
                  Cerrar sesión
                </button>
              </div>
            )}
            <CartBadge />
          </div>
        </div>
      </header>
      <main className="container mx-auto px-4 py-8">
        <Outlet />
      </main>
      <CartDrawer />
    </div>
  )
}
