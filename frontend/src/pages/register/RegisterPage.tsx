import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Card } from '@/shared/components/Card'
import { Input } from '@/shared/components/Input'
import { Button } from '@/shared/components/Button'
import { registerUser, loginUser } from '@/features/auth'
import { useAuthStore } from '@/shared/lib/stores'
import type { AxiosError } from 'axios'

interface FormValues {
  nombre: string
  apellido: string
  email: string
  password: string
  confirmPassword: string
}

interface FormErrors {
  nombre?: string
  apellido?: string
  email?: string
  password?: string
  confirmPassword?: string
  form?: string
}

function validateEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

export function RegisterPage() {
  const navigate = useNavigate()
  const login = useAuthStore((s) => s.login)

  const [values, setValues] = useState<FormValues>({
    nombre: '',
    apellido: '',
    email: '',
    password: '',
    confirmPassword: '',
  })
  const [errors, setErrors] = useState<FormErrors>({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  function validate(): FormErrors {
    const errs: FormErrors = {}
    if (!values.nombre) {
      errs.nombre = 'El nombre es requerido'
    } else if (values.nombre.length < 2) {
      errs.nombre = 'El nombre debe tener al menos 2 caracteres'
    }
    if (!values.apellido) {
      errs.apellido = 'El apellido es requerido'
    } else if (values.apellido.length < 2) {
      errs.apellido = 'El apellido debe tener al menos 2 caracteres'
    }
    if (!values.email) {
      errs.email = 'El email es requerido'
    } else if (!validateEmail(values.email)) {
      errs.email = 'Ingresá un email válido'
    }
    if (!values.password) {
      errs.password = 'La contraseña es requerida'
    } else if (values.password.length < 8) {
      errs.password = 'La contraseña debe tener al menos 8 caracteres'
    }
    if (!values.confirmPassword) {
      errs.confirmPassword = 'Confirmá tu contraseña'
    } else if (values.confirmPassword !== values.password) {
      errs.confirmPassword = 'Las contraseñas no coinciden'
    }
    return errs
  }

  function handleChange(field: keyof FormValues) {
    return (e: React.ChangeEvent<HTMLInputElement>) => {
      setValues((prev) => ({ ...prev, [field]: e.target.value }))
      if (errors[field]) {
        setErrors((prev) => ({ ...prev, [field]: undefined }))
      }
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const validationErrors = validate()
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors)
      return
    }

    setIsSubmitting(true)
    setErrors({})

    try {
      // Register returns only UserResponse (no tokens) — must login afterwards
      await registerUser(values.nombre, values.apellido, values.email, values.password)

      // Auto-login after successful registration
      const { data: tokenData } = await loginUser(values.email, values.password)
      const { api } = await import('@/shared/api')
      api.defaults.headers.common['Authorization'] = `Bearer ${tokenData.access_token}`
      const meResponse = await api.get('/auth/me')
      login(meResponse.data, tokenData.access_token, tokenData.refresh_token)
      navigate('/', { replace: true })
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      const status = axiosError.response?.status
      if (status === 409) {
        setErrors({ form: 'El email ya está registrado. Intentá con otro.' })
      } else if (axiosError.response?.data?.detail) {
        setErrors({ form: axiosError.response.data.detail })
      } else {
        setErrors({ form: 'Ocurrió un error al registrarte. Intentá de nuevo más tarde.' })
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <Card className="w-full max-w-md p-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Crear cuenta</h1>

        <form onSubmit={handleSubmit} noValidate>
          <div className="space-y-4">
            <Input
              label="Nombre"
              id="nombre"
              type="text"
              autoComplete="given-name"
              value={values.nombre}
              onChange={handleChange('nombre')}
              error={errors.nombre}
              aria-invalid={!!errors.nombre}
              disabled={isSubmitting}
            />

            <Input
              label="Apellido"
              id="apellido"
              type="text"
              autoComplete="family-name"
              value={values.apellido}
              onChange={handleChange('apellido')}
              error={errors.apellido}
              aria-invalid={!!errors.apellido}
              disabled={isSubmitting}
            />

            <Input
              label="Email"
              id="email"
              type="email"
              autoComplete="email"
              value={values.email}
              onChange={handleChange('email')}
              error={errors.email}
              aria-invalid={!!errors.email}
              disabled={isSubmitting}
            />

            <Input
              label="Contraseña"
              id="password"
              type="password"
              autoComplete="new-password"
              value={values.password}
              onChange={handleChange('password')}
              error={errors.password}
              aria-invalid={!!errors.password}
              disabled={isSubmitting}
              helperText="Mínimo 8 caracteres"
            />

            <Input
              label="Confirmar contraseña"
              id="confirmPassword"
              type="password"
              autoComplete="new-password"
              value={values.confirmPassword}
              onChange={handleChange('confirmPassword')}
              error={errors.confirmPassword}
              aria-invalid={!!errors.confirmPassword}
              disabled={isSubmitting}
            />
          </div>

          {errors.form && (
            <p role="alert" className="mt-4 text-sm text-red-600">
              {errors.form}
            </p>
          )}

          <Button
            type="submit"
            className="w-full mt-6 bg-orange-500 hover:bg-orange-600 focus:ring-orange-500"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Creando cuenta...' : 'Crear cuenta'}
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-gray-600">
          ¿Ya tenés cuenta?{' '}
          <Link to="/login" className="text-orange-500 hover:text-orange-600 font-medium">
            Iniciá sesión
          </Link>
        </p>
      </Card>
    </div>
  )
}
