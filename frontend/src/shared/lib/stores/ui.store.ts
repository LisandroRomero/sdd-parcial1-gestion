import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export type ToastType = 'success' | 'error' | 'info'

export interface Toast {
  message: string
  type: ToastType
}

export interface UIState {
  sidebarOpen: boolean
  theme: 'light' | 'dark'
  activeModal: string | null
  toast: Toast | null
  toggleSidebar: () => void
  setSidebar: (open: boolean) => void
  setTheme: (theme: 'light' | 'dark') => void
  openModal: (modalId: string) => void
  closeModal: () => void
  showToast: (message: string, type: ToastType) => void
  hideToast: () => void
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      sidebarOpen: true,
      theme: 'light',
      activeModal: null,
      toast: null,

      toggleSidebar: () =>
        set((state) => ({ sidebarOpen: !state.sidebarOpen })),

      setSidebar: (open) =>
        set({ sidebarOpen: open }),

      setTheme: (theme) =>
        set({ theme }),

      openModal: (modalId) =>
        set({ activeModal: modalId }),

      closeModal: () =>
        set({ activeModal: null }),

      showToast: (message, type) =>
        set({ toast: { message, type } }),

      hideToast: () =>
        set({ toast: null }),
    }),
    {
      name: 'food-store-ui',
      version: 1,
      partialize: (state) => ({
        sidebarOpen: state.sidebarOpen,
        theme: state.theme,
      }),
    },
  ),
)

export const uiStore = useUIStore
