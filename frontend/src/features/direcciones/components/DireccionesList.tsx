import { useState, type ReactNode } from 'react'
import { Card, CardHeader, CardContent } from '@/shared/components/Card'
import { Button } from '@/shared/components/Button'
import { ErrorMessage } from '@/shared/ui/ErrorMessage'
import { EmptyState } from '@/shared/ui/EmptyState'
import { getErrorMessage } from '@/shared/api'
import { useUIStore } from '@/shared/lib/stores/ui.store'
import { useDirecciones, useEliminarDireccion, useMarcarPrincipal } from '../hooks/useDirecciones'
import { DireccionCard } from './DireccionCard'
import { DireccionFormModal } from './DireccionFormModal'
import { DeleteConfirmDialog } from './DeleteConfirmDialog'
import type { DireccionEntregaRead } from '@/entities/direcciones'

export function DireccionesList() {
  const { data: direcciones, isLoading, isError, error, refetch } = useDirecciones()
  const [editingDireccion, setEditingDireccion] = useState<DireccionEntregaRead | null>(null)
  const [isCreating, setIsCreating] = useState(false)
  const [deletingId, setDeletingId] = useState<number | null>(null)
  const showToast = useUIStore((s) => s.showToast)
  const eliminarMutation = useEliminarDireccion()
  const marcarPrincipalMutation = useMarcarPrincipal()

  const handleDelete = () => {
    if (deletingId === null) return
    eliminarMutation.mutate(deletingId, {
      onSuccess: () => {
        showToast('Dirección eliminada', 'success')
        setDeletingId(null)
      },
      onError: (err) => {
        showToast(getErrorMessage(err), 'error')
      },
    })
  }

  const handleSetPrincipal = (id: number) => {
    marcarPrincipalMutation.mutate(id, {
      onError: (err) => {
        showToast(getErrorMessage(err), 'error')
      },
    })
  }

  let content: ReactNode

  if (isLoading) {
    content = (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <Card key={i}>
            <CardHeader>
              <div className="h-5 bg-gray-200 rounded animate-pulse w-1/3" />
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="h-4 bg-gray-200 rounded animate-pulse w-3/4" />
                <div className="h-4 bg-gray-200 rounded animate-pulse w-1/2" />
                <div className="h-4 bg-gray-200 rounded animate-pulse w-1/3" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    )
  } else if (isError) {
    content = <ErrorMessage message={getErrorMessage(error)} onRetry={refetch} />
  } else if (!direcciones || direcciones.length === 0) {
    content = (
      <EmptyState
        title="No tenés direcciones guardadas"
        description="Agregá una dirección para recibir tus pedidos"
        action={<Button onClick={() => setIsCreating(true)}>Agregar dirección</Button>}
      />
    )
  } else {
    content = (
      <div>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold">Mis direcciones</h2>
          <Button onClick={() => setIsCreating(true)}>Agregar dirección</Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {direcciones.map((d) => (
            <DireccionCard
              key={d.id}
              direccion={d}
              onEdit={setEditingDireccion}
              onDelete={(id) => setDeletingId(id)}
              onSetPrincipal={handleSetPrincipal}
            />
          ))}
        </div>
      </div>
    )
  }

  return (
    <>
      {content}

      <DireccionFormModal
        isOpen={isCreating || editingDireccion !== null}
        onClose={() => {
          setIsCreating(false)
          setEditingDireccion(null)
        }}
        direccion={editingDireccion}
      />

      <DeleteConfirmDialog
        isOpen={deletingId !== null}
        onCancel={() => setDeletingId(null)}
        onConfirm={handleDelete}
        isDeleting={eliminarMutation.isPending}
      />
    </>
  )
}
