import { Navigate, Outlet } from 'react-router-dom'
import { useAuthStore } from '@/shared/lib/stores/auth.store'

interface RoleGuardProps {
  /** Single role code required to access the route (e.g. 'ADMIN'). */
  role?: string
  /** Multiple role codes — user needs at least one (OR logic). */
  roles?: string[]
}

/**
 * RoleGuard — wraps routes that require a specific role (or one of many).
 *
 * Usage (React Router v6):
 *   <Route element={<RoleGuard role="ADMIN" />}>
 *     <Route path="/admin" element={<AdminPanel />} />
 *   </Route>
 *
 * Redirects to /403 when the user lacks the required role.
 * Assumes the user is already authenticated (use inside a ProtectedRoute).
 */
export function RoleGuard({ role, roles }: RoleGuardProps) {
  const hasRole = useAuthStore((state) => state.hasRole)

  const required = role ? [role] : (roles ?? [])
  const hasAccess = required.length === 0 || required.some((r) => hasRole(r))

  if (!hasAccess) {
    return <Navigate to="/403" replace />
  }

  return <Outlet />
}
