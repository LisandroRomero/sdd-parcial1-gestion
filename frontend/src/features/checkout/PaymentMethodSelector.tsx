import { useQuery } from '@tanstack/react-query'
import { getFormasPago } from '@/shared/api/formas-pago.api'
import { ErrorMessage } from '@/shared/ui'

interface PaymentMethodSelectorProps {
  selected: string
  onSelect: (codigo: string) => void
}

export function PaymentMethodSelector({ selected, onSelect }: PaymentMethodSelectorProps) {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['formas-pago'],
    queryFn: getFormasPago,
    staleTime: 5 * 60 * 1000,
  })

  if (isLoading) {
    return (
      <div className="space-y-3">
        <h3 className="text-lg font-semibold text-gray-900">Método de pago</h3>
        <div className="animate-pulse space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-12 bg-gray-100 rounded-lg" />
          ))}
        </div>
      </div>
    )
  }

  if (isError || !data) {
    return (
      <div className="space-y-3">
        <h3 className="text-lg font-semibold text-gray-900">Método de pago</h3>
        <ErrorMessage
          message="No se pudieron cargar los métodos de pago"
          compact
        />
        <label className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 cursor-pointer">
          <input
            type="radio"
            name="forma_pago"
            value="EFECTIVO"
            checked={selected === 'EFECTIVO'}
            onChange={() => onSelect('EFECTIVO')}
            className="h-4 w-4 text-primary accent-primary"
          />
          <span className="text-sm font-medium text-gray-900">Efectivo</span>
        </label>
      </div>
    )
  }

  const paymentMethods = data.filter((m) => m.activo)

  return (
    <div className="space-y-3">
      <h3 className="text-lg font-semibold text-gray-900">Método de pago</h3>
      <div className="space-y-2">
        {paymentMethods.map((pm) => (
          <label
            key={pm.codigo}
            className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
              selected === pm.codigo
                ? 'border-primary bg-primary/5 ring-1 ring-primary'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <input
              type="radio"
              name="forma_pago"
              value={pm.codigo}
              checked={selected === pm.codigo}
              onChange={() => onSelect(pm.codigo)}
              className="h-4 w-4 text-primary accent-primary"
            />
            <span className="text-sm font-medium text-gray-900">
              {pm.descripcion ?? pm.codigo}
            </span>
          </label>
        ))}
      </div>
    </div>
  )
}
