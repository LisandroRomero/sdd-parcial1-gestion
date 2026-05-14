import { NavLink } from 'react-router-dom'
import { PanelLeftClose, PanelLeftOpen } from 'lucide-react'
import type { NavSection } from './navigation.types'

interface SidebarProps {
  collapsed: boolean
  onToggle: () => void
  sections: NavSection[]
}

export function Sidebar({ collapsed, onToggle, sections }: SidebarProps) {
  return (
    <aside
      className={`max-md:hidden fixed top-0 left-0 z-40 flex flex-col bg-white h-screen transition-all duration-200 ${
        collapsed ? 'w-16' : 'w-64'
      }`}
    >
      <div className="flex items-center justify-between px-4 h-16">
        <h1 className="text-lg font-bold text-gray-900">
          {collapsed ? 'FS' : 'Food Store'}
        </h1>
        <button
          onClick={onToggle}
          className="flex items-center justify-center p-1.5 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
          aria-label={collapsed ? 'Expandir sidebar' : 'Colapsar sidebar'}
        >
          {collapsed ? <PanelLeftOpen size={18} /> : <PanelLeftClose size={18} />}
        </button>
      </div>
      <div className="flex-1 overflow-y-auto py-4 px-3 space-y-6">
        {sections.map((section, idx) => (
          <div key={idx}>
            {section.title && !collapsed && (
              <p className="px-3 mb-2 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                {section.title}
              </p>
            )}
            <div className="space-y-1">
              {section.items.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === '/'}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                      collapsed ? 'justify-center px-2' : ''
                    } ${
                      isActive
                        ? 'bg-primary/10 text-primary font-semibold'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`
                  }
                >
                  {item.icon && <item.icon className="size-5 shrink-0" />}
                  {!collapsed && <span>{item.label}</span>}
                </NavLink>
              ))}
            </div>
          </div>
        ))}
      </div>
    </aside>
  )
}
