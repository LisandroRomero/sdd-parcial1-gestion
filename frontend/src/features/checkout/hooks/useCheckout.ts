import { useMutation, useQueryClient } from '@tanstack/react-query'
import { createPedido } from '@/entities/pedidos'
import { useCartStore } from '@/shared/lib/stores/cart.store'
import { useUIStore } from '@/shared/lib/stores/ui.store'
import { getErrorMessage } from '@/shared/api'
import type { PedidoCreate, PedidoRead } from '@/entities/pedidos'

export function useCheckout() {
  const clearCart = useCartStore((s) => s.clearCart)
  const showToast = useUIStore((s) => s.showToast)
  const queryClient = useQueryClient()

  return useMutation<PedidoRead, Error, PedidoCreate>({
    mutationFn: (data) => createPedido(data),
    onSuccess: (_data) => {
      clearCart()
      queryClient.invalidateQueries({ queryKey: ['pedidos'] })
      showToast('Pedido creado con éxito', 'success')
    },
    onError: (error) => {
      showToast(getErrorMessage(error), 'error')
    },
  })
}
