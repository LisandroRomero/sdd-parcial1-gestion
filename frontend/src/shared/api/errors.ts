import { AxiosError } from 'axios'

const HTTP_ERROR_MESSAGES: Record<number, string> = {
  400: 'Datos inválidos. Revisá los campos e intentá de nuevo.',
  403: 'No tenés permisos para esta acción.',
  404: 'Recurso no encontrado.',
  429: 'Demasiadas solicitudes. Esperá un momento e intentá de nuevo.',
  500: 'Error interno del servidor. Intentá de nuevo más tarde.',
}

export function getErrorMessage(error: unknown): string {
  if (error instanceof AxiosError) {
    // Usar detail del backend si está disponible
    const detail = error.response?.data?.detail
    if (detail && typeof detail === 'string') return detail

    // Fallback por código HTTP
    const status = error.response?.status
    if (status) {
      return HTTP_ERROR_MESSAGES[status] ?? HTTP_ERROR_MESSAGES[500]
    }

    // Sin respuesta del servidor
    return 'Sin conexión. Verificá tu red e intentá de nuevo.'
  }
  return 'Ocurrió un error inesperado.'
}
