import { RouterProvider } from 'react-router-dom'
import { router } from './router'
import { ErrorBoundary } from '../shared/components/ErrorBoundary'

export function Providers() {
  return (
    <ErrorBoundary>
      <RouterProvider router={router} />
    </ErrorBoundary>
  )
}