import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { RouterLoader } from './router'
import { ErrorBoundary } from '../shared/components/ErrorBoundary'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 1000 * 60, // 1 minute
    },
  },
})

export function Providers() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <RouterLoader />
      </QueryClientProvider>
    </ErrorBoundary>
  )
}