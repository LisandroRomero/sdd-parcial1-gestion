import { Card, CardHeader, CardContent, CardFooter } from '@/shared/components/Card'
import { Button } from '@/shared/components/Button'
import type { DireccionEntregaRead } from '@/entities/direcciones'

interface DireccionCardProps {
  direccion: DireccionEntregaRead
  onEdit: (d: DireccionEntregaRead) => void
  onDelete: (id: number) => void
  onSetPrincipal: (id: number) => void
}

export function DireccionCard({ direccion, onEdit, onDelete, onSetPrincipal }: DireccionCardProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-lg">{direccion.alias}</h3>
          {direccion.es_principal && (
            <span className="bg-primary text-white text-xs px-2 py-1 rounded-full font-medium">
              Principal
            </span>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-1">
        <p className="text-gray-700">
          {direccion.calle} {direccion.numero}
          {direccion.piso ? `, Piso ${direccion.piso}` : ''}
          {direccion.departamento ? `, Depto. ${direccion.departamento}` : ''}
        </p>
        <p className="text-gray-500 text-sm">
          {direccion.ciudad}, {direccion.provincia}
        </p>
        <p className="text-gray-500 text-sm">CP: {direccion.codigo_postal}</p>
      </CardContent>
      <CardFooter>
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" size="sm" onClick={() => onEdit(direccion)}>
            Editar
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onDelete(direccion.id)}
            className="text-danger"
          >
            Eliminar
          </Button>
          {!direccion.es_principal && (
            <Button variant="primary" size="sm" onClick={() => onSetPrincipal(direccion.id)}>
              Marcar como principal
            </Button>
          )}
        </div>
      </CardFooter>
    </Card>
  )
}
