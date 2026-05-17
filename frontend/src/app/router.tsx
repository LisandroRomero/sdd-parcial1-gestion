import { createBrowserRouter, Navigate, RouterProvider } from 'react-router-dom'
import { lazy, Suspense } from 'react'
import { Layout } from './routes/layout'
import { LoadingSpinner } from '../shared/ui/LoadingSpinner'
import { ProtectedRoute, AdminRoute } from '@/features/auth'
import { PublicOnlyRoute } from '@/features/auth'

const HomePage = lazy(() => import('./routes/home').then(m => ({ default: m.HomePage })))
const LoginPage = lazy(() => import('../pages/login').then(m => ({ default: m.LoginPage })))
const RegisterPage = lazy(() => import('../pages/register').then(m => ({ default: m.RegisterPage })))
const CatalogoPage = lazy(() => import('../pages/catalogo').then(m => ({ default: m.CatalogoPage })))
const ProductoDetallePage = lazy(() => import('../pages/catalogo').then(m => ({ default: m.ProductoDetallePage })))
const PerfilPage = lazy(() => import('../pages/perfil').then(m => ({ default: m.PerfilPage })))
const CheckoutPage = lazy(() => import('../pages/checkout').then(m => ({ default: m.CheckoutPage })))
const PedidoDetailPage = lazy(() => import('../pages/pedidos').then(m => ({ default: m.PedidoDetailPage })))
const PedidoListPage = lazy(() => import('../pages/pedidos').then(m => ({ default: m.PedidoListPage })))
const AdminUsuariosPage = lazy(() => import('../pages/admin/AdminUsuariosPage').then(m => ({ default: m.AdminUsuariosPage })))
const AdminProductosPage = lazy(() => import('../pages/admin/AdminProductosPage').then(m => ({ default: m.AdminProductosPage })))
const AdminCategoriasPage = lazy(() => import('../pages/admin/AdminCategoriasPage').then(m => ({ default: m.AdminCategoriasPage })))
const AdminIngredientesPage = lazy(() => import('../pages/admin/AdminIngredientesPage').then(m => ({ default: m.AdminIngredientesPage })))
const AdminConfiguracionPage = lazy(() => import('../pages/admin/AdminConfiguracionPage').then(m => ({ default: m.AdminConfiguracionPage })))
const AdminPedidosPage = lazy(() => import('../pages/admin/AdminPedidosPage').then(m => ({ default: m.AdminPedidosPage })))
const AdminPedidoDetailPage = lazy(() => import('../pages/admin/AdminPedidoDetailPage').then(m => ({ default: m.AdminPedidoDetailPage })))

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
          { path: 'pedidos', element: <PedidoListPage /> },
          { path: 'pedidos/:id', element: <PedidoDetailPage /> },
        ],
      },
    ],
  },
  // Admin routes (requires ADMIN role)
  {
    path: '/admin',
    element: <AdminRoute />,
    children: [
      {
        element: <Layout />,
        children: [
          { path: 'usuarios', element: <AdminUsuariosPage /> },
          { path: 'productos', element: <AdminProductosPage /> },
          { path: 'categorias', element: <AdminCategoriasPage /> },
          { path: 'ingredientes', element: <AdminIngredientesPage /> },
          { path: 'configuracion', element: <AdminConfiguracionPage /> },
          { path: 'pedidos', element: <AdminPedidosPage /> },
          { path: 'pedidos/:id', element: <AdminPedidoDetailPage /> },
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
