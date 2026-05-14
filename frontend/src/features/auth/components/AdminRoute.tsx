import { Navigate, Outlet } from 'react-router-dom'
import { useAuthStore } from '@/shared/lib/stores/auth.store'

/**
 * AdminRoute — wraps routes that require authentication AND the ADMIN role.
 *
 * Usage (React Router v6):
 *   <Route element={<AdminRoute />}>
 *     <Route path="/admin/usuarios" element={<AdminUsuariosPage />} />
 *   </Route>
 *
 * Redirects to /login when unauthenticated, or to / when authenticated but
 * without the ADMIN role.
 */
export function AdminRoute() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const user = useAuthStore((state) => state.user)

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  const isAdmin = user?.roles.includes('ADMIN') ?? false
  if (!isAdmin) {
    return <Navigate to="/" replace />
  }

  return <Outlet />
}
