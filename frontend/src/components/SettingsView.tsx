import React, { useState } from 'react'
import {
  AlertTriangle,
  CheckCircle,
  Database,
  Download,
  Lock,
  RefreshCw,
  RotateCcw,
  Shield,
  Trash2,
} from 'lucide-react'
import { AIStatus } from '../api/types'

interface SettingsViewProps {
  aiStatus: AIStatus | null
  onOpenDiagnostics: () => void
  onSeedData: () => Promise<void>
  onResetData: () => Promise<void>
  onExportData: () => Promise<void>
}

export const SettingsView: React.FC<SettingsViewProps> = ({
  aiStatus,
  onOpenDiagnostics,
  onSeedData,
  onResetData,
  onExportData,
}) => {
  const [confirmReset, setConfirmReset] = useState(false)
  const [busy, setBusy] = useState(false)

  const handleSeed = async () => {
    setBusy(true)
    try {
      await onSeedData()
      alert('Demo data successfully seeded (8 journal entries, 9 memories, 1 future self note).')
    } finally {
      setBusy(false)
    }
  }

  const handleReset = async () => {
    setBusy(true)
    try {
      await onResetData()
      setConfirmReset(false)
      alert('All local memories and journals have been deleted.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', maxWidth: '800px' }}>
      <div>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 700 }}>Settings & Data Sovereignty</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          Anchor is 100% local-first. You own every byte of your data.
        </p>
      </div>

      {/* Local AI Status Card */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
            <Shield size={20} color="#7b93fc" />
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Local AI Engine</h3>
          </div>
          <button className="btn btn-secondary btn-sm" onClick={onOpenDiagnostics}>
            View Diagnostics
          </button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', fontSize: '0.85rem' }}>
          <div style={{ padding: '0.75rem', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ color: 'var(--text-muted)' }}>Runtime</div>
            <div style={{ fontWeight: 600 }}>{aiStatus?.runtime || 'Ollama'} (127.0.0.1:11434)</div>
          </div>
          <div style={{ padding: '0.75rem', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ color: 'var(--text-muted)' }}>Configured Model</div>
            <div style={{ fontWeight: 600 }}>{aiStatus?.model || 'gemma3:4b'}</div>
          </div>
          <div style={{ padding: '0.75rem', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ color: 'var(--text-muted)' }}>AI Status</div>
            <div style={{ fontWeight: 600, color: aiStatus?.ready ? 'var(--success)' : 'var(--warning)' }}>
              {aiStatus?.ready ? 'Ready (Local)' : 'Offline / Standby'}
            </div>
          </div>
        </div>
      </div>

      {/* Memory Controls */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '1rem' }}>
          <Database size={20} color="#34d399" />
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Data & Memory Controls</h3>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.75rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
            <div>
              <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>Export Data (JSON)</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                Download an unencrypted, complete copy of all your journal entries, memories, and provenance links.
              </div>
            </div>
            <button className="btn btn-secondary btn-sm" onClick={onExportData}>
              <Download size={14} />
              <span>Export All</span>
            </button>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.75rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
            <div>
              <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>Reseed Demo Data</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                Populates 8 fictional journal entries (June–October) and 9 memories for testing and demonstration.
              </div>
            </div>
            <button className="btn btn-secondary btn-sm" onClick={handleSeed} disabled={busy}>
              <RotateCcw size={14} />
              <span>{busy ? 'Seeding...' : 'Reseed Demo Data'}</span>
            </button>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.75rem 0' }}>
            <div>
              <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--danger)' }}>Delete All Local Data</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                Irreversibly delete all memories, vectors, journals, and reflections from your local machine.
              </div>
            </div>
            <button
              className="btn btn-danger btn-sm"
              onClick={() => setConfirmReset(true)}
              disabled={busy}
            >
              <Trash2 size={14} />
              <span>Delete All Data</span>
            </button>
          </div>
        </div>
      </div>

      {/* Privacy Guarantees */}
      <div className="card" style={{ background: 'rgba(80, 110, 229, 0.03)', border: '1px solid rgba(80, 110, 229, 0.2)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '0.75rem' }}>
          <Lock size={18} color="#7b93fc" />
          <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>Privacy Architecture</h3>
        </div>
        <ul style={{ paddingLeft: '1.25rem', fontSize: '0.82rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
          <li>No telemetry, no remote trackers, no analytics.</li>
          <li>Database is stored strictly in your local SQLite directory (<code>anchor.db</code>).</li>
          <li>Inference is executed exclusively through your local Ollama daemon. No cloud APIs.</li>
          <li>No automated cloud fallbacks exist in this software. Ever.</li>
        </ul>
      </div>

      {/* Confirmation Modal for Reset */}
      {confirmReset && (
        <div className="modal-overlay" onClick={() => setConfirmReset(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem', color: 'var(--danger)' }}>
              <AlertTriangle size={24} />
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Are you absolutely sure?</h3>
            </div>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginBottom: '1.5rem', lineHeight: 1.6 }}>
              This will permanently delete all saved memories, journal entries, conversations, and vector records. This action cannot be undone.
            </p>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
              <button className="btn btn-ghost" onClick={() => setConfirmReset(false)}>
                Cancel
              </button>
              <button className="btn btn-danger" onClick={handleReset} disabled={busy}>
                Yes, Delete Everything
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
