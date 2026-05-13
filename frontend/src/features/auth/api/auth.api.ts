import { api } from '@/shared/api'
import type { User } from '@/shared/lib/stores'

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface RegisterResponse extends User {
  created_at: string | null
}

/**
 * Authenticate user and receive JWT token pair.
 */
export const loginUser = (email: string, password: string) =>
  api.post<LoginResponse>('/auth/login', { email, password })

/**
 * Register a new user account (returns UserResponse, no tokens).
 * Must call loginUser() afterwards to obtain tokens.
 */
export const registerUser = (
  nombre: string,
  apellido: string,
  email: string,
  password: string,
) => api.post<RegisterResponse>('/auth/register', { nombre, apellido, email, password })

/**
 * Revoke the current refresh token to close the session.
 * Requires the refresh token in the request body.
 */
export const logoutUser = (refreshToken: string) =>
  api.post('/auth/logout', { refresh_token: refreshToken })
