import { useForm } from '@tanstack/react-form'
import { Card, CardHeader, CardContent } from '@/shared/components/Card'
import { Input } from '@/shared/components/Input'
import { Button } from '@/shared/components/Button'
import { useActualizarPerfil } from '@/features/perfil/hooks/usePerfil'
import { useUIStore } from '@/shared/lib/stores'
import type { PerfilRead } from '@/entities/perfil'

interface ProfileFormProps {
  perfil: PerfilRead
}

export function ProfileForm({ perfil }: ProfileFormProps) {
  const showToast = useUIStore((s) => s.showToast)
  const mutation = useActualizarPerfil()

  const form = useForm({
    defaultValues: {
      nombre: perfil.nombre ?? '',
      apellido: perfil.apellido ?? '',
      telefono: perfil.telefono ?? '',
    },
    onSubmit: async ({ value }) => {
      try {
        await mutation.mutateAsync({
          nombre: value.nombre || null,
          apellido: value.apellido || null,
          telefono: value.telefono || null,
        })
        showToast('Datos actualizados correctamente', 'success')
      } catch {
        showToast('Error al actualizar los datos', 'error')
      }
    },
  })

  return (
    <Card>
      <CardHeader>
        <h2 className="text-xl font-semibold text-gray-900">Mis Datos</h2>
      </CardHeader>
      <CardContent>
        <form
          onSubmit={(e) => {
            e.preventDefault()
            e.stopPropagation()
            form.handleSubmit()
          }}
        >
          <div className="space-y-4">
            <form.Field
              name="nombre"
              validators={{
                onChange: ({ value }) => {
                  if (value.length < 2) return 'El nombre debe tener al menos 2 caracteres'
                  if (value.length > 80) return 'El nombre no puede superar los 80 caracteres'
                  return undefined
                },
              }}
            >
              {(field) => (
                <Input
                  label="Nombre"
                  id="nombre"
                  value={field.state.value}
                  onChange={(e) => field.handleChange(e.target.value)}
                  onBlur={field.handleBlur}
                  error={field.state.meta.errors?.[0]}
                  disabled={form.state.isSubmitting}
                />
              )}
            </form.Field>

            <form.Field
              name="apellido"
              validators={{
                onChange: ({ value }) => {
                  if (value.length < 2) return 'El apellido debe tener al menos 2 caracteres'
                  if (value.length > 80) return 'El apellido no puede superar los 80 caracteres'
                  return undefined
                },
              }}
            >
              {(field) => (
                <Input
                  label="Apellido"
                  id="apellido"
                  value={field.state.value}
                  onChange={(e) => field.handleChange(e.target.value)}
                  onBlur={field.handleBlur}
                  error={field.state.meta.errors?.[0]}
                  disabled={form.state.isSubmitting}
                />
              )}
            </form.Field>

            <Input
              label="Email"
              id="email"
              type="email"
              value={perfil.email}
              className="bg-gray-100 cursor-not-allowed"
              disabled
            />

            <form.Field
              name="telefono"
              validators={{
                onChange: () => undefined,
              }}
            >
              {(field) => (
                <Input
                  label="Teléfono"
                  id="telefono"
                  type="tel"
                  value={field.state.value}
                  onChange={(e) => field.handleChange(e.target.value)}
                  onBlur={field.handleBlur}
                  error={field.state.meta.errors?.[0]}
                  disabled={form.state.isSubmitting}
                />
              )}
            </form.Field>
          </div>

          <Button
            type="submit"
            className="mt-6 bg-orange-500 hover:bg-orange-600 focus:ring-orange-500"
            disabled={form.state.isSubmitting}
          >
            {form.state.isSubmitting ? 'Guardando...' : 'Guardar cambios'}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
