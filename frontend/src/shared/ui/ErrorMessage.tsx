interface ErrorMessageProps {
  message: string
  onRetry?: () => void
  compact?: boolean
  className?: string
}

export function ErrorMessage({ message, onRetry, compact = false, className = '' }: ErrorMessageProps) {
  return (
    <div
      className={`flex flex-col items-start gap-2 rounded-lg border border-red-200 bg-red-50 p-4 text-left ${compact ? 'p-3' : ''} ${className}`}
      role="alert"
    >
      <div className="flex items-center gap-2 text-red-700">
        <svg className="h-5 w-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <span className={`font-medium text-red-800 ${compact ? 'text-sm' : ''}`}>{message}</span>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="text-sm font-medium text-red-700 underline underline-offset-2 hover:text-red-800"
        >
          Reintentar
        </button>
      )}
    </div>
  )
}
