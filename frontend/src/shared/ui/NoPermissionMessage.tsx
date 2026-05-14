import { Link } from 'react-router-dom'

interface NoPermissionMessageProps {
  status?: 401 | 403
  className?: string
}

export function NoPermissionMessage({ status = 403, className = '' }: NoPermissionMessageProps) {
  const isUnauthorized = status === 401

  return (
    <div className={`rounded-lg border border-slate-200 bg-slate-50 p-4 text-left ${className}`} role="alert">
      <p className="font-medium text-slate-900">
        {isUnauthorized ? 'Necesitás iniciar sesión' : 'No tenés permisos para ver esto'}
      </p>
      <p className="mt-1 text-sm text-slate-600">
        {isUnauthorized
          ? 'Tu sesión no está activa o expiró.'
          : 'Tu cuenta no tiene acceso a esta sección.'}
      </p>
      <div className="mt-3 flex gap-3">
        {isUnauthorized ? (
          <Link to="/login" className="text-sm font-medium text-primary underline underline-offset-2">
            Iniciar sesión
          </Link>
        ) : (
          <Link to="/" className="text-sm font-medium text-primary underline underline-offset-2">
            Volver al inicio
          </Link>
        )}
      </div>
    </div>
  )
}
