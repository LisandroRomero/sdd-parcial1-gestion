import { useState, useRef } from 'react'
import { statusLabels } from '@/entities/pedidos/constants'

const ESTADOS = Object.entries(statusLabels) as [string, string][]

interface FilterValues {
  estado?: string
  fecha_desde?: string
  fecha_hasta?: string
  buscar?: string
}

interface OrderFiltersProps {
  onFilterChange: (filters: FilterValues) => void
}

export function OrderFilters({ onFilterChange }: OrderFiltersProps) {
  const [estado, setEstado] = useState('')
  const [fechaDesde, setFechaDesde] = useState('')
  const [fechaHasta, setFechaHasta] = useState('')
  const [buscar, setBuscar] = useState('')
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  function applyFilters(overrides: Partial<FilterValues> = {}) {
    const current = {
      estado: estado || undefined,
      fecha_desde: fechaDesde || undefined,
      fecha_hasta: fechaHasta || undefined,
      buscar: buscar || undefined,
      ...overrides,
    }
    onFilterChange(current)
  }

  function clearFilters() {
    setEstado('')
    setFechaDesde('')
    setFechaHasta('')
    setBuscar('')
    onFilterChange({})
  }

  function handleBuscarChange(value: string) {
    setBuscar(value)
    if (debounceRef.current) clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => {
      onFilterChange({
        estado: estado || undefined,
        fecha_desde: fechaDesde || undefined,
        fecha_hasta: fechaHasta || undefined,
        buscar: value || undefined,
      })
    }, 400)
  }

  const hasFilters = estado || fechaDesde || fechaHasta || buscar

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
      {/* Search input — full width row */}
      <div className="mb-3">
        <label htmlFor="filter-buscar" className="block text-xs font-medium text-gray-500 mb-1">
          Buscar
        </label>
        <input
          id="filter-buscar"
          type="text"
          value={buscar}
          onChange={(e) => handleBuscarChange(e.target.value)}
          placeholder="Buscar por N° de pedido..."
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
        />
      </div>

      <div className="flex flex-wrap items-end gap-3">
        {/* Estado filter */}
        <div className="flex-1 min-w-[150px]">
          <label htmlFor="filter-estado" className="block text-xs font-medium text-gray-500 mb-1">
            Estado
          </label>
          <select
            id="filter-estado"
            value={estado}
            onChange={(e) => setEstado(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent bg-white"
          >
            <option value="">Todos</option>
            {ESTADOS.map(([codigo, label]) => (
              <option key={codigo} value={codigo}>
                {label}
              </option>
            ))}
          </select>
        </div>

        {/* Fecha desde */}
        <div className="flex-1 min-w-[150px]">
          <label htmlFor="filter-fecha-desde" className="block text-xs font-medium text-gray-500 mb-1">
            Desde
          </label>
          <input
            id="filter-fecha-desde"
            type="date"
            value={fechaDesde}
            onChange={(e) => setFechaDesde(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
          />
        </div>

        {/* Fecha hasta */}
        <div className="flex-1 min-w-[150px]">
          <label htmlFor="filter-fecha-hasta" className="block text-xs font-medium text-gray-500 mb-1">
            Hasta
          </label>
          <input
            id="filter-fecha-hasta"
            type="date"
            value={fechaHasta}
            onChange={(e) => setFechaHasta(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
          />
        </div>

        {/* Action buttons */}
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => applyFilters()}
            className="px-4 py-2 bg-primary text-white text-sm font-medium rounded-lg hover:bg-primary-dark transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
          >
            Filtrar
          </button>
          {hasFilters && (
            <button
              type="button"
              onClick={clearFilters}
              className="px-4 py-2 text-gray-600 text-sm font-medium rounded-lg border border-gray-300 hover:bg-gray-50 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2"
            >
              Limpiar
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
