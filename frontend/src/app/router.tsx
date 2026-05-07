import { createBrowserRouter, Navigate, RouterProvider } from 'react-router-dom'
import { lazy, Suspense } from 'react'
import { Layout } from './routes/layout'
import { LoadingSpinner } from '../shared/ui/LoadingSpinner'

const HomePage = lazy(() => import('./routes/home').then(m => ({ default: m.HomePage })))

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        index: true,
        element: <HomePage />,
      },
      {
        path: '*',
        element: <Navigate to="/" replace />,
      },
    ],
  },
])

export function RouterLoader() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center min-h-screen"><LoadingSpinner /></div>}>
      <RouterProvider router={router} />
    </Suspense>
  )
}