import { useDirecciones } from '@/features/direcciones'
import { Card, CardHeader, CardContent } from '@/shared/components'
import { Button } from '@/shared/components'
import { ErrorMessage, EmptyState, LoadingSpinner } from '@/shared/ui'
import { useNavigate } from 'react-router-dom'
import type { DireccionEntregaRead } from '@/entities/direcciones'
import { getErrorMessage } from '@/shared/api'

interface AddressSelectorProps {
  selectedId: number | null
  onSelect: (direccion: DireccionEntregaRead) => void
}

export function AddressSelector({ selectedId, onSelect }: AddressSelectorProps) {
  const navigate = useNavigate()
  const { data: direcciones, isLoading, isError, error, refetch } = useDirecciones()

  if (isLoading) {
    return (
      <Card>
        <CardHeader><h3 className="text-lg font-semibold">Dirección de entrega</h3></CardHeader>
        <CardContent><LoadingSpinner /></CardContent>
      </Card>
    )
  }

  if (isError) {
    return (
      <Card>
        <CardHeader><h3 className="text-lg font-semibold">Dirección de entrega</h3></CardHeader>
        <CardContent>
          <ErrorMessage message={getErrorMessage(error)} onRetry={refetch} />
        </CardContent>
      </Card>
    )
  }

  if (!direcciones || direcciones.length === 0) {
    return (
      <Card>
        <CardHeader><h3 className="text-lg font-semibold">Dirección de entrega</h3></CardHeader>
        <CardContent>
          <EmptyState
            title="No tenés direcciones guardadas"
            description="Agregá una dirección en tu perfil antes de confirmar el pedido"
            action={<Button variant="outline" onClick={() => navigate('/perfil')}>Ir a mi perfil</Button>}
          />
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <h3 className="text-lg font-semibold">Dirección de entrega</h3>
        <p className="text-sm text-gray-500">Seleccioná dónde querés recibir tu pedido</p>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {direcciones.map((d) => {
            const direccionCompleta = [d.calle, d.numero, d.piso ? `Piso ${d.piso}` : '', d.departamento ? `Depto ${d.departamento}` : '', d.ciudad, d.provincia].filter(Boolean).join(', ')
            return (
              <button
                key={d.id}
                type="button"
                onClick={() => onSelect(d)}
                className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                  selectedId === d.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300 bg-white'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      {d.alias && <span className="font-medium text-gray-900">{d.alias}</span>}
                      {d.es_principal && (
                        <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-medium">
                          Principal
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mt-1">{direccionCompleta}</p>
                    <p className="text-sm text-gray-500">{d.codigo_postal}</p>
                  </div>
                  {selectedId === d.id && (
                    <span className="text-blue-600 text-xl leading-none mt-1">✓</span>
                  )}
                </div>
              </button>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
