import type { ComponentType } from 'react'

export interface NavItem {
  label: string
  to: string
  icon?: ComponentType<{ className?: string }>
  requiresAuth?: boolean
  roles?: string[]
  getLabel?: (roles: string[]) => string
}

export interface NavSection {
  title?: string
  items: NavItem[]
}
