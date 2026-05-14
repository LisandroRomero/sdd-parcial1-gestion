import { usePerfil } from '@/features/perfil/hooks/usePerfil'
import { ProfileForm } from '@/features/perfil/components/ProfileForm'
import { DireccionesList } from '@/features/direcciones/components/DireccionesList'
import { ErrorMessage, EmptyState } from '@/shared/ui'
import { Card, CardHeader, CardContent } from '@/shared/components/Card'
import { getErrorMessage } from '@/shared/api'

export function PerfilPage() {
  const { data: perfil, isLoading, isError, error, refetch } = usePerfil()

  if (isLoading) {
    return (
      <div>
        <div className="h-8 w-32 bg-gray-200 rounded animate-pulse mb-8" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <Card>
            <CardHeader>
              <div className="h-6 w-24 bg-gray-200 rounded animate-pulse" />
            </CardHeader>
            <CardContent className="space-y-4">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-10 bg-gray-200 rounded animate-pulse" />
              ))}
              <div className="h-10 w-40 bg-gray-200 rounded animate-pulse mt-6" />
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <div className="h-6 w-32 bg-gray-200 rounded animate-pulse" />
            </CardHeader>
            <CardContent>
              {[...Array(2)].map((_, i) => (
                <div key={i} className="h-24 bg-gray-200 rounded animate-pulse mb-4" />
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  if (isError) {
    return (
      <ErrorMessage
        message={getErrorMessage(error)}
        onRetry={refetch}
      />
    )
  }

  if (!perfil) {
    return (
      <EmptyState
        title="No se pudo cargar el perfil"
        description="No encontramos información de tu perfil. Intentá recargar la página."
        action={<button className="text-primary underline underline-offset-2" onClick={refetch}>Reintentar</button>}
      />
    )
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-8">Mi Perfil</h1>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <ProfileForm perfil={perfil} />
        <DireccionesList />
      </div>
    </div>
  )
}
