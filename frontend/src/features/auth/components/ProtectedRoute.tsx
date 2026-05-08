import { Navigate, Outlet } from 'react-router-dom'
import { useAuthStore } from '@/shared/lib/stores/auth.store'

/**
 * ProtectedRoute — wraps routes that require authentication.
 *
 * Usage (React Router v6):
 *   <Route element={<ProtectedRoute />}>
 *     <Route path="/dashboard" element={<Dashboard />} />
 *   </Route>
 *
 * Redirects to /login when the user is not authenticated.
 */
export function ProtectedRoute() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}
