import type { AxiosError } from 'axios'

type ErrorShape = { detail?: string }

export function getAuthErrorStatus(error: unknown): 401 | 403 | undefined {
  const axiosError = error as AxiosError<ErrorShape> | undefined
  const status = axiosError?.response?.status

  if (status === 401 || status === 403) {
    return status
  }

  return undefined
}
