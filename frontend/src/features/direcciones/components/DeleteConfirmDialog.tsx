import { Button } from '@/shared/components/Button'

interface DeleteConfirmDialogProps {
  isOpen: boolean
  onCancel: () => void
  onConfirm: () => void
  isDeleting?: boolean
}

export function DeleteConfirmDialog({ isOpen, onCancel, onConfirm, isDeleting }: DeleteConfirmDialogProps) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-white rounded-xl shadow-lg w-full max-w-sm mx-4 p-6">
        <h3 className="text-lg font-semibold mb-2">Eliminar dirección</h3>
        <p className="text-gray-600 mb-6">
          ¿Estás seguro que querés eliminar esta dirección?
        </p>
        <div className="flex justify-end gap-3">
          <Button type="button" variant="outline" onClick={onCancel} disabled={isDeleting}>
            Cancelar
          </Button>
          <Button
            type="button"
            variant="ghost"
            onClick={onConfirm}
            disabled={isDeleting}
            className="bg-red-600 text-white hover:bg-red-700"
          >
            {isDeleting ? 'Eliminando...' : 'Eliminar'}
          </Button>
        </div>
      </div>
    </div>
  )
}
