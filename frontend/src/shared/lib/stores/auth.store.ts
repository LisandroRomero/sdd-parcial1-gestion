import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface User {
  id: number
  email: string
  nombre: string | null
  apellido: string | null
  roles: string[]  // e.g. ['CLIENT', 'ADMIN', 'STOCK', 'PEDIDOS']
}

export interface AuthState {
  user: User | null
  token: string | null           // access token
  refreshToken: string | null    // refresh token — NO persistido
  isAuthenticated: boolean
  login: (user: User, accessToken: string, refreshToken: string) => void
  logout: () => void
  updateUser: (user: User) => void
  setTokens: (accessToken: string, refreshToken: string) => void
  hasRole: (role: string) => boolean
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      login: (user, accessToken, refreshToken) =>
        set({ user, token: accessToken, refreshToken, isAuthenticated: true }),
      logout: () =>
        set({ user: null, token: null, refreshToken: null, isAuthenticated: false }),
      updateUser: (user) => set({ user }),
      setTokens: (accessToken, refreshToken) =>
        set({ token: accessToken, refreshToken }),
      hasRole: (role: string) => {
        const { user } = get()
        if (!user) return false
        return user.roles.includes(role)
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)

export const authStore = useAuthStore
