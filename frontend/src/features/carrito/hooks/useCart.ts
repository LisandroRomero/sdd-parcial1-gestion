import { useCartStore } from '@/shared/lib/stores/cart.store'

export function useCart() {
  const store = useCartStore()
  return {
    ...store,
    isInCart: (productoId: number) =>
      store.items.some((i) => i.productoId === productoId),
    getItemCount: (productoId: number) =>
      store.items.find((i) => i.productoId === productoId)?.cantidad ?? 0,
  }
}
