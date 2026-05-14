import { ReactNode } from 'react'

interface EmptyStateProps {
  icon?: ReactNode
  title: string
  description?: string
  action?: ReactNode
  compact?: boolean
  className?: string
}

export function EmptyState({ icon, title, description, action, compact = false, className = '' }: EmptyStateProps) {
  return (
    <div className={`flex flex-col items-center justify-center px-4 text-center ${compact ? 'py-8' : 'py-12'} ${className}`}>
      {icon && <div className="mb-4 text-gray-400">{icon}</div>}
      <h3 className={`${compact ? 'text-base' : 'text-lg'} font-medium text-gray-900 mb-1`}>{title}</h3>
      {description && <p className={`text-gray-500 mb-4 max-w-sm ${compact ? 'text-sm' : ''}`}>{description}</p>}
      {action && <div>{action}</div>}
    </div>
  )
}
