interface OfflineMessageProps {
  className?: string
}

export function OfflineMessage({ className = '' }: OfflineMessageProps) {
  return (
    <div className={`rounded-lg border border-amber-200 bg-amber-50 p-4 text-left ${className}`} role="status">
      <p className="font-medium text-amber-900">Estás sin conexión</p>
      <p className="mt-1 text-sm text-amber-800">
        Revisá tu red y volvé a intentar cuando se restablezca la conexión.
      </p>
    </div>
  )
}
