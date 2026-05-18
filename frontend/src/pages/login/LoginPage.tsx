import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Card } from '@/shared/components/Card'
import { Input } from '@/shared/components/Input'
import { Button } from '@/shared/components/Button'
import { useAuthStore } from '@/shared/lib/stores'
import { loginUser } from '@/features/auth'
import type { AxiosError } from 'axios'

interface FormValues {
  email: string
  password: string
}

interface FormErrors {
  email?: string
  password?: string
  form?: string
}

function validateEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

export function LoginPage() {
  const navigate = useNavigate()
  const login = useAuthStore((s) => s.login)

  const [values, setValues] = useState<FormValues>({ email: '', password: '' })
  const [errors, setErrors] = useState<FormErrors>({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  function validate(): FormErrors {
    const errs: FormErrors = {}
    if (!values.email) {
      errs.email = 'El email es requerido'
    } else if (!validateEmail(values.email)) {
      errs.email = 'Ingresá un email válido'
    }
    if (!values.password) {
      errs.password = 'La contraseña es requerida'
    }
    return errs
  }

  function handleChange(field: keyof FormValues) {
    return (e: React.ChangeEvent<HTMLInputElement>) => {
      setValues((prev) => ({ ...prev, [field]: e.target.value }))
      // Clear field error on change
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
      const { data } = await loginUser(values.email, values.password)
      // The backend doesn't return user data in login — fetch it via /auth/me
      // For now, construct a minimal user from the token or use a separate /me call.
      // We need to call /auth/me to get user data after login.
      const { api } = await import('@/shared/api')
      api.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`
      const meResponse = await api.get('/auth/me')
      login(meResponse.data, data.access_token, data.refresh_token)
      navigate('/', { replace: true })
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      if (axiosError.response?.status === 401) {
        setErrors({ form: 'Email o contraseña incorrectos' })
      } else {
        setErrors({ form: 'Ocurrió un error. Intentá de nuevo más tarde.' })
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-amber-50 via-orange-50 to-rose-50">
      <div className="flex flex-col items-center">
        <div className="mb-6 text-center">
          <span className="text-4xl">🍕</span>
        </div>
        <Card className="w-full max-w-md p-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Iniciar sesión</h1>

        <form onSubmit={handleSubmit} noValidate>
          <div className="space-y-4">
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
              autoComplete="current-password"
              value={values.password}
              onChange={handleChange('password')}
              error={errors.password}
              aria-invalid={!!errors.password}
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
            className="w-full mt-6 bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 focus:ring-orange-500 text-white font-medium"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Iniciando sesión...' : 'Iniciar sesión'}
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-gray-600">
          ¿No tenés cuenta?{' '}
          <Link to="/register" className="text-primary hover:text-primary-dark font-medium">
            Registrate
          </Link>
        </p>
      </Card>
      </div>
    </div>
  )
}
