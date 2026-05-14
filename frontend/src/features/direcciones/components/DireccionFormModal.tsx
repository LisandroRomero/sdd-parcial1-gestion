import { useEffect } from 'react'
import { useForm } from '@tanstack/react-form'
import { Button } from '@/shared/components/Button'
import { Input } from '@/shared/components/Input'
import { useUIStore } from '@/shared/lib/stores/ui.store'
import { getErrorMessage } from '@/shared/api'
import { useCrearDireccion, useActualizarDireccion } from '../hooks/useDirecciones'
import type { DireccionEntregaRead, DireccionEntregaCreate, DireccionEntregaUpdate } from '@/entities/direcciones'

interface DireccionFormModalProps {
  isOpen: boolean
  onClose: () => void
  direccion?: DireccionEntregaRead | null
}

export function DireccionFormModal({ isOpen, onClose, direccion }: DireccionFormModalProps) {
  const showToast = useUIStore((s) => s.showToast)
  const crearMutation = useCrearDireccion()
  const actualizarMutation = useActualizarDireccion()

  const isEditing = !!direccion
  const isSaving = crearMutation.isPending || actualizarMutation.isPending

  const form = useForm({
    defaultValues: {
      alias: '',
      calle: '',
      numero: '',
      piso: '',
      departamento: '',
      ciudad: '',
      provincia: '',
      codigo_postal: '',
    },
    onSubmit: async ({ value }) => {
      if (isEditing && direccion) {
        const payload: DireccionEntregaUpdate = {
          alias: value.alias,
          calle: value.calle,
          numero: value.numero,
          piso: value.piso || null,
          departamento: value.departamento || null,
          ciudad: value.ciudad,
          provincia: value.provincia,
          codigo_postal: value.codigo_postal,
        }
        actualizarMutation.mutate(
          { id: direccion.id, data: payload },
          {
            onSuccess: () => {
              showToast('Dirección actualizada', 'success')
              onClose()
            },
            onError: (err) => {
              showToast(getErrorMessage(err), 'error')
            },
          },
        )
      } else {
        const payload: DireccionEntregaCreate = {
          alias: value.alias,
          calle: value.calle,
          numero: value.numero,
          piso: value.piso || null,
          departamento: value.departamento || null,
          ciudad: value.ciudad,
          provincia: value.provincia,
          codigo_postal: value.codigo_postal,
        }
        crearMutation.mutate(payload, {
          onSuccess: () => {
            showToast('Dirección agregada', 'success')
            onClose()
          },
          onError: (err) => {
            showToast(getErrorMessage(err), 'error')
          },
        })
      }
    },
  })

  useEffect(() => {
    if (!isOpen) return
    if (direccion) {
      form.reset({
        alias: direccion.alias,
        calle: direccion.calle,
        numero: direccion.numero,
        piso: direccion.piso ?? '',
        departamento: direccion.departamento ?? '',
        ciudad: direccion.ciudad,
        provincia: direccion.provincia,
        codigo_postal: direccion.codigo_postal,
      })
    } else {
      form.reset()
    }
  }, [direccion, isOpen])

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-white rounded-xl shadow-lg w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
        <form
          onSubmit={(e) => {
            e.preventDefault()
            e.stopPropagation()
            form.handleSubmit()
          }}
        >
          <div className="p-6 space-y-4">
            <h2 className="text-xl font-semibold">
              {isEditing ? 'Editar dirección' : 'Nueva dirección'}
            </h2>

            <form.Field
              name="alias"
              validators={{
                onChange: ({ value }) => {
                  if (!value.trim()) return 'El alias es obligatorio'
                  return undefined
                },
              }}
            >
              {(field) => (
                <Input
                  label="Alias"
                  id="alias"
                  value={field.state.value}
                  onChange={(e) => field.handleChange(e.target.value)}
                  onBlur={field.handleBlur}
                  error={field.state.meta.errors?.[0]}
                  disabled={isSaving}
                  placeholder="Ej: Casa, Trabajo"
                />
              )}
            </form.Field>

            <div className="grid grid-cols-2 gap-4">
              <form.Field
                name="calle"
                validators={{
                  onChange: ({ value }) => {
                    if (!value.trim()) return 'La calle es obligatoria'
                    return undefined
                  },
                }}
              >
                {(field) => (
                  <Input
                    label="Calle"
                    id="calle"
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    onBlur={field.handleBlur}
                    error={field.state.meta.errors?.[0]}
                    disabled={isSaving}
                  />
                )}
              </form.Field>

              <form.Field
                name="numero"
                validators={{
                  onChange: ({ value }) => {
                    if (!value.trim()) return 'El número es obligatorio'
                    return undefined
                  },
                }}
              >
                {(field) => (
                  <Input
                    label="Número"
                    id="numero"
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    onBlur={field.handleBlur}
                    error={field.state.meta.errors?.[0]}
                    disabled={isSaving}
                  />
                )}
              </form.Field>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <form.Field name="piso">
                {(field) => (
                  <Input
                    label="Piso (opcional)"
                    id="piso"
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    onBlur={field.handleBlur}
                    disabled={isSaving}
                  />
                )}
              </form.Field>

              <form.Field name="departamento">
                {(field) => (
                  <Input
                    label="Departamento (opcional)"
                    id="departamento"
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    onBlur={field.handleBlur}
                    disabled={isSaving}
                  />
                )}
              </form.Field>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <form.Field
                name="ciudad"
                validators={{
                  onChange: ({ value }) => {
                    if (!value.trim()) return 'La ciudad es obligatoria'
                    return undefined
                  },
                }}
              >
                {(field) => (
                  <Input
                    label="Ciudad"
                    id="ciudad"
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    onBlur={field.handleBlur}
                    error={field.state.meta.errors?.[0]}
                    disabled={isSaving}
                  />
                )}
              </form.Field>

              <form.Field
                name="provincia"
                validators={{
                  onChange: ({ value }) => {
                    if (!value.trim()) return 'La provincia es obligatoria'
                    return undefined
                  },
                }}
              >
                {(field) => (
                  <Input
                    label="Provincia"
                    id="provincia"
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    onBlur={field.handleBlur}
                    error={field.state.meta.errors?.[0]}
                    disabled={isSaving}
                  />
                )}
              </form.Field>
            </div>

            <form.Field
              name="codigo_postal"
              validators={{
                onChange: ({ value }) => {
                  if (!value.trim()) return 'El código postal es obligatorio'
                  return undefined
                },
              }}
            >
              {(field) => (
                <Input
                  label="Código postal"
                  id="codigo_postal"
                  value={field.state.value}
                  onChange={(e) => field.handleChange(e.target.value)}
                  onBlur={field.handleBlur}
                  error={field.state.meta.errors?.[0]}
                  disabled={isSaving}
                />
              )}
            </form.Field>
          </div>

          <div className="flex justify-end gap-3 px-6 pb-6">
            <Button type="button" variant="outline" onClick={onClose} disabled={isSaving}>
              Cancelar
            </Button>
            <Button type="submit" variant="primary" disabled={isSaving}>
              {isSaving
                ? 'Guardando...'
                : isEditing
                  ? 'Guardar cambios'
                  : 'Crear dirección'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}
