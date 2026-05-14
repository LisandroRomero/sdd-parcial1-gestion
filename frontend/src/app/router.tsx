import { createBrowserRouter, Navigate, RouterProvider } from 'react-router-dom'
import { lazy, Suspense } from 'react'
import { Layout } from './routes/layout'
import { LoadingSpinner } from '../shared/ui/LoadingSpinner'
import { ProtectedRoute } from '@/features/auth'
import { PublicOnlyRoute } from '@/features/auth'

const HomePage = lazy(() => import('./routes/home').then(m => ({ default: m.HomePage })))
const LoginPage = lazy(() => import('../pages/login').then(m => ({ default: m.LoginPage })))
const RegisterPage = lazy(() => import('../pages/register').then(m => ({ default: m.RegisterPage })))
const CatalogoPage = lazy(() => import('../pages/catalogo').then(m => ({ default: m.CatalogoPage })))
const ProductoDetallePage = lazy(() => import('../pages/catalogo').then(m => ({ default: m.ProductoDetallePage })))
const PerfilPage = lazy(() => import('../pages/perfil').then(m => ({ default: m.PerfilPage })))
const CheckoutPage = lazy(() => import('../pages/checkout').then(m => ({ default: m.CheckoutPage })))

export const router = createBrowserRouter([
  // Public-only routes (redirect to / if already authenticated)
  {
    element: <PublicOnlyRoute />,
    children: [
      { path: '/login', element: <LoginPage /> },
      { path: '/register', element: <RegisterPage /> },
    ],
  },
  // Public routes with Layout (no auth required)
  {
    element: <Layout />,
    children: [
      { path: '/catalogo', element: <CatalogoPage /> },
      { path: '/catalogo/:id', element: <ProductoDetallePage /> },
    ],
  },
  // Protected routes (redirect to /login if not authenticated)
  {
    path: '/',
    element: <ProtectedRoute />,
    children: [
      {
        element: <Layout />,
        children: [
          { index: true, element: <HomePage /> },
          { path: 'perfil', element: <PerfilPage /> },
          { path: 'checkout', element: <CheckoutPage /> },
        ],
      },
    ],
  },
  // Catch-all at root level — only fires for truly unmatched routes
  {
    path: '*',
    element: <Navigate to="/" replace />,
  },
])

export function RouterLoader() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center min-h-screen"><LoadingSpinner /></div>}>
      <RouterProvider router={router} />
    </Suspense>
  )
}
