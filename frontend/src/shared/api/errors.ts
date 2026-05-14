import { AxiosError } from 'axios'

type Rfc7807Error = {
  detail?: string
  errors?: Array<{ field?: string; message?: string; code?: string }>
  requestId?: string
}

const HTTP_ERROR_MESSAGES: Record<number, string> = {
  400: 'Datos inválidos. Revisá los campos e intentá de nuevo.',
  401: 'Sesión expirada. Iniciá sesión de nuevo.',
  403: 'No tenés permisos para esta acción.',
  404: 'Recurso no encontrado.',
  409: 'Conflicto con el estado actual del recurso.',
  422: 'Error de validación. Revisá los datos ingresados.',
  429: 'Demasiadas solicitudes. Esperá un momento e intentá de nuevo.',
  500: 'Error interno del servidor. Intentá de nuevo más tarde.',
}

export function getErrorMessage(error: unknown): string {
  if (error instanceof AxiosError) {
    const data = error.response?.data as Rfc7807Error | undefined
    const validationMessage = data?.errors?.[0]?.message
    if (validationMessage) return validationMessage

    const detail = data?.detail
    if (detail && typeof detail === 'string') return detail

    const status = error.response?.status
    if (status) {
      return HTTP_ERROR_MESSAGES[status] ?? HTTP_ERROR_MESSAGES[500]
    }

    return 'Sin conexión. Verificá tu red e intentá de nuevo.'
  }
  return 'Ocurrió un error inesperado.'
}

export function getErrorRequestId(error: unknown): string | undefined {
  if (error instanceof AxiosError) {
    const data = error.response?.data as Rfc7807Error | undefined
    return data?.requestId
  }
  return undefined
}
