import {
  Package,
  LayoutDashboard,
  ClipboardList,
  User,
  Users,
  ShoppingBag,
  Tags,
  Utensils,
  Settings,
} from 'lucide-react'
import type { NavSection } from './navigation.types'

export const navigationSections: NavSection[] = [
  {
    items: [
      {
        label: 'Catálogo',
        to: '/catalogo',
        icon: Package,
      },
      {
        label: 'Dashboard',
        to: '/',
        icon: LayoutDashboard,
        requiresAuth: true,
      },
      {
        label: 'Pedidos',
        to: '/pedidos',
        icon: ClipboardList,
        requiresAuth: true,
        getLabel: (roles) => (roles.includes('CLIENT') ? 'Mis Pedidos' : 'Pedidos'),
      },
      {
        label: 'Mi Perfil',
        to: '/perfil',
        icon: User,
        requiresAuth: true,
      },
    ],
  },
  {
    title: 'Administración',
    items: [
      {
        label: 'Usuarios',
        to: '/admin/usuarios',
        icon: Users,
        requiresAuth: true,
        roles: ['ADMIN'],
      },
      {
        label: 'Productos',
        to: '/admin/productos',
        icon: ShoppingBag,
        requiresAuth: true,
        roles: ['ADMIN'],
      },
      {
        label: 'Categorías',
        to: '/admin/categorias',
        icon: Tags,
        requiresAuth: true,
        roles: ['ADMIN'],
      },
      {
        label: 'Ingredientes',
        to: '/admin/ingredientes',
        icon: Utensils,
        requiresAuth: true,
        roles: ['ADMIN'],
      },
      {
        label: 'Configuración',
        to: '/admin/configuracion',
        icon: Settings,
        requiresAuth: true,
        roles: ['ADMIN'],
      },
      {
        label: 'Pedidos',
        to: '/admin/pedidos',
        icon: ClipboardList,
        requiresAuth: true,
        roles: ['ADMIN'],
      },
    ],
  },
]
