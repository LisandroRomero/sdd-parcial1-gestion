import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { DetallePedidoCreate } from '@/entities/pedidos'

export interface CartItem {
  id: string
  productoId: number
  nombre: string
  precio_base: string // Decimal comes as string from API
  cantidad: number
  imagenUrl?: string
  ingredientesExcluidos: number[]
}

export interface AddProductInput {
  id: number
  nombre: string
  precio_base: string // Decimal comes as string from API
  imagenUrl?: string
}

export interface CartState {
  items: CartItem[]
  totalItems: number
  totalPrice: number
  isCartEmpty: boolean
  addItem: (
    product: AddProductInput,
    cantidad: number,
    personalizacion?: { ingredientesExcluidos?: number[] },
  ) => void
  removeItem: (itemId: string) => void
  updateQuantity: (itemId: string, cantidad: number) => void
  updateCustomization: (itemId: string, ingredientesExcluidos: number[]) => void
  toggleIngrediente: (itemId: string, ingredienteId: number) => void
  clearCart: () => void
  getItemsForCheckout: () => DetallePedidoCreate[]
}

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
}

function recompute(items: CartItem[]) {
  return {
    totalItems: items.reduce((sum, item) => sum + item.cantidad, 0),
    totalPrice: items.reduce(
      (sum, item) => sum + parseFloat(item.precio_base) * item.cantidad,
      0,
    ),
    isCartEmpty: items.length === 0,
  }
}

export const useCartStore = create<CartState>()(
  persist(
    (set, get) => ({
      items: [],
      totalItems: 0,
      totalPrice: 0,
      isCartEmpty: true,

      addItem: (product, cantidad, personalizacion) => {
        const { items } = get()
        const excludidos = personalizacion?.ingredientesExcluidos ?? []
        const existingIndex = items.findIndex(
          (item) =>
            item.productoId === product.id &&
            JSON.stringify(item.ingredientesExcluidos) ===
              JSON.stringify(excludidos),
        )

        if (existingIndex !== -1) {
          const updated = [...items]
          updated[existingIndex] = {
            ...updated[existingIndex],
            cantidad: updated[existingIndex].cantidad + cantidad,
          }
          set({ items: updated, ...recompute(updated) })
        } else {
          const newItem: CartItem = {
            id: generateId(),
            productoId: product.id,
            nombre: product.nombre,
            precio_base: product.precio_base,
            cantidad,
            imagenUrl: product.imagenUrl,
            ingredientesExcluidos: excludidos,
          }
          const newItems = [...items, newItem]
          set({ items: newItems, ...recompute(newItems) })
        }
      },

      removeItem: (itemId) => {
        const { items } = get()
        const newItems = items.filter((item) => item.id !== itemId)
        set({ items: newItems, ...recompute(newItems) })
      },

      updateQuantity: (itemId, cantidad) => {
        const { items } = get()
        if (cantidad <= 0) {
          const newItems = items.filter((item) => item.id !== itemId)
          set({ items: newItems, ...recompute(newItems) })
          return
        }
        const newItems = items.map((item) =>
          item.id === itemId ? { ...item, cantidad } : item,
        )
        set({ items: newItems, ...recompute(newItems) })
      },

      updateCustomization: (itemId, ingredientesExcluidos) => {
        const { items } = get()
        const newItems = items.map((item) =>
          item.id === itemId ? { ...item, ingredientesExcluidos } : item,
        )
        set({ items: newItems, ...recompute(newItems) })
      },

      toggleIngrediente: (itemId, ingredienteId) => {
        const { items } = get()
        const newItems = items.map((item) => {
          if (item.id !== itemId) return item
          const excludidos = item.ingredientesExcluidos
          const isExcluded = excludidos.includes(ingredienteId)
          return {
            ...item,
            ingredientesExcluidos: isExcluded
              ? excludidos.filter((id) => id !== ingredienteId)
              : [...excludidos, ingredienteId],
          }
        })
        set({ items: newItems, ...recompute(newItems) })
      },

      clearCart: () => set({ items: [], ...recompute([]) }),

      getItemsForCheckout: () => {
        const { items } = get()
        return items.map((item) => ({
          producto_id: item.productoId,
          cantidad: item.cantidad,
          ...(item.ingredientesExcluidos.length > 0 && { personalizacion: item.ingredientesExcluidos }),
        }))
      },
    }),
    {
      name: 'food-store-cart',
      version: 2,
      partialize: (state) => ({
        items: state.items,
      }),
      merge: (persisted, current) => {
        const items = (persisted as any)?.items ?? []
        return {
          ...current,
          items,
          ...recompute(items),
        }
      },
      migrate: (persisted, version) => {
        if (version < 2) {
          const oldState = persisted as any
          return { items: oldState.items ?? [] } as CartState
        }
        return persisted as CartState
      },
    },
  ),
)

export const cartStore = useCartStore
