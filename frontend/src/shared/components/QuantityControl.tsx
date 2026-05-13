import type { ChangeEvent } from 'react'

interface QuantityControlProps {
  value: number
  onChange: (v: number) => void
  min?: number
  max?: number
}

export function QuantityControl({ value, onChange, min = 1, max }: QuantityControlProps) {
  const handleDecrement = () => {
    if (value > min) onChange(value - 1)
  }

  const handleIncrement = () => {
    if (max === undefined || value < max) onChange(value + 1)
  }

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const parsed = parseInt(e.target.value, 10)
    if (isNaN(parsed)) return
    const clamped = max !== undefined ? Math.min(max, Math.max(min, parsed)) : Math.max(min, parsed)
    onChange(clamped)
  }

  return (
    <div className="inline-flex items-center rounded-lg border border-gray-300 overflow-hidden">
      <button
        type="button"
        aria-label="Disminuir cantidad"
        onClick={handleDecrement}
        disabled={value <= min}
        className="px-2.5 py-1.5 text-gray-600 hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary"
      >
        −
      </button>
      <input
        type="number"
        aria-label="Cantidad"
        value={value}
        min={min}
        max={max}
        onChange={handleInputChange}
        className="w-12 text-center text-sm font-medium border-x border-gray-300 py-1.5 focus:outline-none focus:ring-2 focus:ring-primary [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
      />
      <button
        type="button"
        aria-label="Aumentar cantidad"
        onClick={handleIncrement}
        disabled={max !== undefined && value >= max}
        className="px-2.5 py-1.5 text-gray-600 hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary"
      >
        +
      </button>
    </div>
  )
}
