import { useEffect, useRef } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Input } from '@/shared/components'
import { useCategorias } from '../hooks/useCategorias'

export function CatalogFilters() {
  const [searchParams, setSearchParams] = useSearchParams()
  const { data: categoriasData } = useCategorias()

  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const busqueda = searchParams.get('busqueda') ?? ''
  const categoriaId = searchParams.get('categoria_id') ?? ''
  const precioMin = searchParams.get('precio_min') ?? ''
  const precioMax = searchParams.get('precio_max') ?? ''
  const tieneAlergenos = searchParams.get('tiene_alergenos') === 'true'

  function setParam(key: string, value: string | undefined) {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev)
      if (value === undefined || value === '') {
        next.delete(key)
      } else {
        next.set(key, value)
      }
      next.set('page', '1')
      return next
    })
  }

  function handleBusquedaChange(e: React.ChangeEvent<HTMLInputElement>) {
    const value = e.target.value
    if (debounceRef.current) clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => {
      setParam('busqueda', value)
    }, 300)
  }

  function handleLimpiar() {
    setSearchParams({ page: '1' })
  }

  // cleanup debounce on unmount
  useEffect(() => {
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current)
    }
  }, [])

  const categorias = categoriasData?.items ?? []

  return (
    <div className="bg-white rounded-2xl border border-amber-100 shadow-sm p-5 space-y-4">
      <h2 className="font-semibold text-gray-900 text-sm uppercase tracking-wide">Filtros</h2>

      {/* Búsqueda */}
      <div>
        <Input
          label="Buscar"
          placeholder="Nombre del producto..."
          defaultValue={busqueda}
          onChange={handleBusquedaChange}
        />
      </div>

      {/* Categoría */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Categoría</label>
        <select
          value={categoriaId}
          onChange={(e) => setParam('categoria_id', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-amber-400 focus:border-transparent bg-white"
        >
          <option value="">Todas las categorías</option>
          {categorias.map((cat) => (
            <option key={cat.id} value={String(cat.id)}>
              {cat.nombre}
            </option>
          ))}
        </select>
      </div>

      {/* Precio */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Precio</label>
        <div className="flex items-center gap-2">
          <input
            type="number"
            placeholder="Mín"
            value={precioMin}
            onChange={(e) => setParam('precio_min', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-amber-400 focus:border-transparent"
            min={0}
          />
          <span className="text-gray-400 text-sm">—</span>
          <input
            type="number"
            placeholder="Máx"
            value={precioMax}
            onChange={(e) => setParam('precio_max', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-amber-400 focus:border-transparent"
            min={0}
          />
        </div>
      </div>

      {/* Alérgenos */}
      <div className="flex items-center gap-2">
        <input
          id="tiene-alergenos"
          type="checkbox"
          checked={tieneAlergenos}
          onChange={(e) => setParam('tiene_alergenos', e.target.checked ? 'true' : '')}
          className="w-4 h-4 accent-amber-500 rounded"
        />
        <label htmlFor="tiene-alergenos" className="text-sm text-gray-700 cursor-pointer">
          Solo productos con alérgenos
        </label>
      </div>

      {/* Limpiar */}
      <button
        onClick={handleLimpiar}
        className="w-full text-sm text-amber-600 hover:text-amber-700 font-medium py-1.5 border border-amber-200 rounded-lg hover:bg-amber-50 transition-colors"
      >
        Limpiar filtros
      </button>
    </div>
  )
}
