import React from 'react'
import {
  Flame,
  Settings,
  ShieldCheck,
} from 'lucide-react'
import { AIStatus } from '../api/types'

interface SidebarProps {
  currentTab: string
  setCurrentTab: (tab: string) => void
  aiStatus: AIStatus | null
  onOpenDiagnostics: () => void
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  setCurrentTab,
  aiStatus,
  onOpenDiagnostics,
}) => {
  const navItems = [
    { id: 'journal-express', label: 'wts on my mind today', icon: Flame },
    { id: 'settings', label: 'Settings', icon: Settings },
  ]

  const getStatusText = () => {
    if (!aiStatus) return 'Connecting...'
    if (aiStatus.ready) return 'LOCAL — Ready'
    if (!aiStatus.runtime_available) return 'LOCAL — Offline'
    if (!aiStatus.model_available) return 'LOCAL — Model unavailable'
    if (!aiStatus.embeddings_available) return 'LOCAL — Embeddings unavailable'
    return 'LOCAL — Starting'
  }

  const getStatusDotClass = () => {
    if (!aiStatus || !aiStatus.runtime_available) return 'status-dot offline'
    if (aiStatus.ready) return 'status-dot ready'
    return 'status-dot warning'
  }

  return (
    <aside className="sidebar">
      <div className="app-header">
        <div className="logo-wrap">
          <Flame size={24} color="var(--accent)" />
          <span className="logo-text">wts on my mind today</span>
        </div>
        <div className="logo-tagline">thoughts & meme reality-check</div>

        <div style={{ marginTop: '0.85rem' }}>
          <button
            className="status-pill"
            onClick={onOpenDiagnostics}
            title="Click to view local AI diagnostics and setup status"
          >
            <span className={getStatusDotClass()} />
            <span>{getStatusText()}</span>
          </button>
        </div>
      </div>

      <nav className="nav-menu">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = currentTab === item.id
          return (
            <button
              key={item.id}
              className={`nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setCurrentTab(item.id)}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </button>
          )
        })}
      </nav>

      <div style={{ padding: '1rem', borderTop: '1px solid var(--border-subtle)', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
        <div>100% Local-First</div>
        <div>No cloud telemetry</div>
      </div>
    </aside>
  )
}
