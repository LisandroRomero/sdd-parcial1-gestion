import { Link } from 'react-router-dom'
import { Utensils, Clock, Star } from 'lucide-react'
import { Button } from '@/shared/components'

export function HomePage() {
  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-primary via-violet-600 to-accent p-8 md:p-12 text-white">
        <div className="relative z-10">
          <h1 className="text-3xl md:text-4xl font-bold">
            Tu comida favorita, a un clic
          </h1>
          <p className="mt-3 text-lg text-white/90 max-w-xl">
            Explorá nuestro catálogo, armá tu pedido y recibilo en la puerta de tu casa.
          </p>
          <Link to="/catalogo">
            <Button
              className="mt-6 bg-white text-primary hover:bg-white/90 font-semibold px-6 shadow-lg"
            >
              Ver catálogo
            </Button>
          </Link>
        </div>
        {/* Decorative circles */}
        <div className="absolute -top-12 -right-12 w-48 h-48 rounded-full bg-white/10" />
        <div className="absolute -bottom-8 -right-4 w-32 h-32 rounded-full bg-white/10" />
        <div className="absolute top-1/2 -left-8 w-24 h-24 rounded-full bg-white/5" />
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <QuickActionCard
          icon={<Utensils className="size-6" />}
          title="Catálogo"
          description="Explorá todos nuestros platos"
          link="/catalogo"
          color="from-amber-500 to-orange-500"
        />
        <QuickActionCard
          icon={<Clock className="size-6" />}
          title="Mis Pedidos"
          description="Seguí el estado de tus pedidos"
          link="/pedidos"
          color="from-blue-500 to-indigo-500"
        />
        <QuickActionCard
          icon={<Star className="size-6" />}
          title="Mi Perfil"
          description="Gestioná tu cuenta y direcciones"
          link="/perfil"
          color="from-emerald-500 to-teal-500"
        />
      </div>
    </div>
  )
}

function QuickActionCard({ icon, title, description, link, color }: {
  icon: React.ReactNode
  title: string
  description: string
  link: string
  color: string
}) {
  return (
    <Link to={link} className="group">
      <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm hover:shadow-md transition-all duration-200 hover:-translate-y-0.5">
        <div className={`inline-flex p-2.5 rounded-lg bg-gradient-to-br ${color} text-white mb-3 shadow-sm`}>
          {icon}
        </div>
        <h3 className="font-semibold text-gray-900 group-hover:text-primary transition-colors">
          {title}
        </h3>
        <p className="text-sm text-gray-500 mt-1">{description}</p>
      </div>
    </Link>
  )
}
