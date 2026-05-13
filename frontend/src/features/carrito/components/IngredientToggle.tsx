import type { ProductoIngredienteRead } from '@/entities/producto'

interface IngredientToggleProps {
  ingrediente: ProductoIngredienteRead
  checked: boolean
  onChange: () => void
}

export function IngredientToggle({ ingrediente, checked, onChange }: IngredientToggleProps) {
  return (
    <label className="flex items-center gap-3 cursor-pointer py-1.5 group">
      <input
        type="checkbox"
        checked={checked}
        onChange={onChange}
        className="w-4 h-4 rounded border-gray-300 text-primary focus:ring-primary cursor-pointer"
      />
      <span className="text-sm text-gray-700 group-hover:text-gray-900 transition-colors select-none">
        {ingrediente.nombre}
        {ingrediente.es_alergeno && (
          <span className="ml-2 text-xs font-medium text-amber-600 bg-amber-50 px-1.5 py-0.5 rounded">
            Alérgeno
          </span>
        )}
      </span>
    </label>
  )
}
