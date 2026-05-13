import { Navigate, Outlet } from 'react-router-dom'
import { useAuthStore } from '@/shared/lib/stores'

/**
 * PublicOnlyRoute — wraps routes that should only be accessible when NOT authenticated.
 *
 * Usage (React Router v6):
 *   <Route element={<PublicOnlyRoute />}>
 *     <Route path="/login" element={<LoginPage />} />
 *     <Route path="/register" element={<RegisterPage />} />
 *   </Route>
 *
 * Redirects to / when the user is already authenticated.
 */
export function PublicOnlyRoute() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  return isAuthenticated ? <Navigate to="/" replace /> : <Outlet />
}
