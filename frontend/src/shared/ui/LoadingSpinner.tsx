interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  label?: string
  className?: string
}

const sizes = {
  sm: 'w-4 h-4',
  md: 'w-8 h-8',
  lg: 'w-12 h-12',
}

export function LoadingSpinner({ size = 'md', label = 'Cargando', className = '' }: LoadingSpinnerProps) {
  return (
    <div className={`flex items-center justify-center ${className}`}>
      <div
        className={`${sizes[size]} border-4 border-gray-200 border-t-primary rounded-full animate-spin`}
        role="status"
        aria-label={label}
      >
        <span className="sr-only">{label}...</span>
      </div>
    </div>
  )
}
