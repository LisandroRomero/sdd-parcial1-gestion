import { useState } from 'react'
import { useListarFormasPago } from '@/features/admin/hooks/useListarFormasPago'
import { useToggleFormaPago } from '@/features/admin/hooks/useToggleFormaPago'
import type { FormaPagoRead } from '@/entities/admin/types'
import { LoadingSpinner, ErrorMessage, EmptyState } from '@/shared/ui'
import { Button } from '@/shared/components'

function EstadoBadge({ activo }: { activo: boolean }) {
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
        activo
          ? 'bg-green-100 text-green-700 ring-1 ring-green-600/20'
          : 'bg-red-100 text-red-700 ring-1 ring-red-600/20'
      }`}
    >
      {activo ? 'Activo' : 'Inactivo'}
    </span>
  )
}

export function AdminConfiguracionPage() {
  const { data, isLoading, isError, error, refetch } = useListarFormasPago()
  const toggleMutation = useToggleFormaPago()

  const [togglingCode, setTogglingCode] = useState<string | null>(null)
  const [toggleError, setToggleError] = useState<string | null>(null)

  function handleToggle(forma: FormaPagoRead) {
    setTogglingCode(forma.codigo)
    setToggleError(null)
    toggleMutation.mutate(
      { codigo: forma.codigo, body: { activo: !forma.activo } },
      {
        onSettled: () => setTogglingCode(null),
        onError: (err) => {
          const msg = err instanceof Error ? err.message : 'Error al actualizar'
          setToggleError(msg)
        },
      },
    )
  }

  if (isLoading && !data) {
    return (
      <div className="flex items-center justify-center py-20">
        <LoadingSpinner />
      </div>
    )
  }

  if (isError && !data) {
    return (
      <ErrorMessage
        message={error instanceof Error ? error.message : 'Error al cargar configuración'}
        onRetry={refetch}
      />
    )
  }

  const formas = data ?? []

  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Configuración</h1>
        <p className="text-sm text-gray-500 mt-1">
          Administrá las opciones operativas del sistema
        </p>
      </div>

      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Formas de pago</h2>
        </div>

        {toggleError && (
          <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
            {toggleError}
          </div>
        )}

        {formas.length === 0 ? (
          <EmptyState
            title="Sin formas de pago"
            description="No hay formas de pago configuradas en el sistema."
          />
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {formas.map((forma) => (
              <div
                key={forma.codigo}
                className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wide">
                      {forma.codigo === 'TARJETA'
                        ? 'Tarjeta'
                        : forma.codigo === 'RAPIPAGO'
                          ? 'Rapipago'
                          : forma.codigo === 'PAGO_FACIL'
                            ? 'Pago Fácil'
                            : forma.codigo}
                    </h3>
                    {forma.descripcion && (
                      <p className="text-xs text-gray-500 mt-0.5">{forma.descripcion}</p>
                    )}
                  </div>
                  <EstadoBadge activo={forma.activo} />
                </div>

                <Button
                  variant={forma.activo ? 'secondary' : 'primary'}
                  size="sm"
                  onClick={() => handleToggle(forma)}
                  disabled={togglingCode === forma.codigo}
                  className="w-full"
                >
                  {togglingCode === forma.codigo
                    ? 'Actualizando…'
                    : forma.activo
                      ? 'Deshabilitar'
                      : 'Habilitar'}
                </Button>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
