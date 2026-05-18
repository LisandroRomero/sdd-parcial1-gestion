export const statusColors: Record<string, string> = {
  PENDIENTE: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  CONFIRMADO: 'bg-blue-100 text-blue-800 border-blue-300',
  EN_PREP: 'bg-purple-100 text-purple-800 border-purple-300',
  EN_CAMINO: 'bg-indigo-100 text-indigo-800 border-indigo-300',
  ENTREGADO: 'bg-green-100 text-green-800 border-green-300',
  CANCELADO: 'bg-red-100 text-red-800 border-red-300',
}

export const statusLabels: Record<string, string> = {
  PENDIENTE: 'Pendiente',
  CONFIRMADO: 'Confirmado',
  EN_PREP: 'En preparación',
  EN_CAMINO: 'En camino',
  ENTREGADO: 'Entregado',
  CANCELADO: 'Cancelado',
}

export const ADMIN_TRANSITIONS: Record<string, string[]> = {
  PENDIENTE: ['CONFIRMADO', 'CANCELADO'],
  CONFIRMADO: ['EN_PREP', 'CANCELADO'],
  EN_PREP: ['EN_CAMINO', 'CANCELADO'],
  EN_CAMINO: ['ENTREGADO'],
  ENTREGADO: [],
  CANCELADO: [],
}

export function getAdminNextStates(currentState: string, roles: string[]): string[] {
  const canAdvance = roles.includes('ADMIN') || roles.includes('PEDIDOS')
  if (!canAdvance) return []
  return ADMIN_TRANSITIONS[currentState] ?? []
}
