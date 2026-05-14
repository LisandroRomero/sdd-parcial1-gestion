import { useEffect, useState, useCallback } from 'react'
import { Button } from '@/shared/components'
import { useCancelarPedido } from '../hooks/useCancelarPedido'
import { useUIStore } from '@/shared/lib/stores/ui.store'

interface CancelarPedidoModalProps {
  pedidoId: number
  isOpen: boolean
  onClose: () => void
  onMutationChange?: (isPending: boolean) => void
}

const MOTIVOS_PREDEFINIDOS = [
  'El cliente canceló',
  'Producto no disponible',
  'Error en el pedido',
  'Problema de stock',
  'Otro',
] as const

export function CancelarPedidoModal({ pedidoId, isOpen, onClose, onMutationChange }: CancelarPedidoModalProps) {
  const [selectedMotivo, setSelectedMotivo] = useState<string>('')
  const [customMotivo, setCustomMotivo] = useState<string>('')
  const showToast = useUIStore((s) => s.showToast)

  const mutation = useCancelarPedido()

  useEffect(() => {
    if (!isOpen) {
      setSelectedMotivo('')
      setCustomMotivo('')
    }
  }, [isOpen])

  useEffect(() => {
    if (!isOpen) return

    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape') onClose()
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, onClose])

  useEffect(() => {
    onMutationChange?.(mutation.isPending)
  }, [mutation.isPending, onMutationChange])

  const motivoFinal = useCallback(() => {
    const base = selectedMotivo
    if (selectedMotivo === 'Otro') return customMotivo.trim()
    if (customMotivo.trim()) return `${base}: ${customMotivo.trim()}`
    return base
  }, [selectedMotivo, customMotivo])

  const handleConfirm = useCallback(() => {
    const motivo = motivoFinal()
    if (!motivo) return

    mutation.mutate(
      { pedidoId, motivo },
      {
        onSuccess: () => {
          showToast('Pedido cancelado exitosamente', 'success')
          onClose()
        },
        onError: (error) => {
          const errorCode = (error as { response?: { data?: { error_code?: string } } })?.response?.data?.error_code
          if (errorCode === 'PEDIDO_ESTADO_TERMINAL') {
            onClose()
          }
        },
      },
    )
  }, [motivoFinal, mutation, pedidoId, showToast, onClose])

  const isPending = mutation.isPending
  const hasReason = selectedMotivo !== '' && (selectedMotivo !== 'Otro' || customMotivo.trim() !== '')
  const isConfirmDisabled = !hasReason || isPending

  if (!isOpen) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      onClick={(e) => { if (e.target === e.currentTarget) onClose() }}
    >
      <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
        <h2 className="mb-2 text-lg font-semibold text-gray-900">Cancelar pedido</h2>
        <p className="mb-4 text-sm text-gray-600">
          Seleccioná el motivo por el cual querés cancelar este pedido. Esta acción no se puede deshacer.
        </p>

        <div className="mb-4 space-y-2">
          {MOTIVOS_PREDEFINIDOS.map((motivo) => (
            <label
              key={motivo}
              className={`flex cursor-pointer items-center gap-3 rounded-lg border px-4 py-3 transition-colors ${
                selectedMotivo === motivo
                  ? 'border-danger bg-danger/5 text-danger'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <input
                type="radio"
                name="motivo"
                value={motivo}
                checked={selectedMotivo === motivo}
                onChange={() => setSelectedMotivo(motivo)}
                disabled={isPending}
                className="h-4 w-4 accent-danger"
              />
              <span className="text-sm font-medium">{motivo}</span>
            </label>
          ))}
        </div>

        <div className="mb-6">
          <textarea
            placeholder={
              selectedMotivo === 'Otro'
                ? 'Describí el motivo...'
                : 'Agregá un detalle adicional (opcional)...'
            }
            value={customMotivo}
            onChange={(e) => setCustomMotivo(e.target.value.slice(0, 255))}
            disabled={isPending}
            rows={3}
            className="w-full resize-none rounded-lg border border-gray-300 px-3 py-2 text-sm transition-colors focus:border-danger focus:outline-none focus:ring-2 focus:ring-danger/20 disabled:opacity-50"
          />
          <p className="mt-1 text-right text-xs text-gray-400">{customMotivo.length}/255</p>
        </div>

        <div className="flex gap-3">
          <Button
            variant="outline"
            className="flex-1"
            onClick={onClose}
            disabled={isPending}
          >
            No, mantener pedido
          </Button>
          <Button
            variant="primary"
            className="flex-1 bg-danger hover:bg-danger-dark focus:ring-danger"
            onClick={handleConfirm}
            disabled={isConfirmDisabled}
          >
            {isPending ? (
              <span className="flex items-center gap-2">
                <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
                </svg>
                Cancelando...
              </span>
            ) : (
              'Sí, cancelar pedido'
            )}
          </Button>
        </div>
      </div>
    </div>
  )
}
