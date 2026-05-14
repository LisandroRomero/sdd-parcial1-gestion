import { useAuthStore } from '@/shared/lib/stores'
import type { NavSection } from './navigation.types'

export function useFilteredNavSections(sections: NavSection[]): NavSection[] {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const user = useAuthStore((s) => s.user)
  const roles = user?.roles ?? []

  return sections
    .map((section) => ({
      ...section,
      items: section.items
        .filter((item) => {
          if (item.requiresAuth && !isAuthenticated) return false
          if (item.roles && !item.roles.some((r) => roles.includes(r))) return false
          return true
        })
        .map((item) => ({
          ...item,
          label: item.getLabel ? item.getLabel(roles) : item.label,
        })),
    }))
    .filter((section) => section.items.length > 0)
}
