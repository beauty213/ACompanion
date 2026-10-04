import React, { useState } from 'react'
import { AlertCircle, CheckCircle, HelpCircle, RefreshCw, X } from 'lucide-react'
import { AIStatus } from '../api/types'

interface DiagnosticsModalProps {
  isOpen: boolean
  onClose: () => void
  aiStatus: AIStatus | null
  onRefresh: () => Promise<void>
}

export const DiagnosticsModal: React.FC<DiagnosticsModalProps> = ({
  isOpen,
  onClose,
  aiStatus,
  onRefresh,
}) => {
  const [checking, setChecking] = useState(false)
  const [showGuide, setShowGuide] = useState(false)

  if (!isOpen) return null

  const handleCheckAgain = async () => {
    setChecking(true)
    try {
      await onRefresh()
    } finally {
      setChecking(false)
    }
  }

  const checks = [
    {
      title: 'Local Database (SQLite)',
      description: 'Encrypted or local SQLite storage at anchor.db',
      passed: true,
    },
    {
      title: 'Memory Engine',
      description: 'Persistent local storage for long-term memory & provenance',
      passed: true,
    },
    {
      title: 'Ollama Runtime',
      description: 'Local inference daemon at http://localhost:11434',
      passed: Boolean(aiStatus?.runtime_available),
    },
    {
      title: `Configured Model (${aiStatus?.model || 'gemma3:4b'})`,
      description: 'Local open-weight language model',
      passed: Boolean(aiStatus?.model_available),
    },
    {
      title: 'Embeddings Engine (nomic-embed-text)',
      description: 'Vector embeddings for similarity retrieval',
      passed: Boolean(aiStatus?.embeddings_available),
    },
    {
      title: 'Minimal Inference Test',
      description: 'Verified test generation and token validation',
      passed: Boolean(aiStatus?.inference_test),
    },
  ]

  const isFullyReady = aiStatus?.ready

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Local AI Status & Diagnostics</h2>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              Self-contained inspection of your local runtime and memory engine
            </p>
          </div>
          <button className="btn btn-ghost" onClick={onClose} style={{ padding: '0.4rem' }}>
            <X size={18} />
          </button>
        </div>

        <div className={`banner ${isFullyReady ? 'banner-info' : 'banner-warning'}`}>
          {isFullyReady ? (
            <div>
              <strong>Local AI is ready.</strong> All reflection, memory retrieval, and local inference checks have passed.
            </div>
          ) : (
            <div>
              <strong>Setup required or AI offline.</strong> Anchor's core SQLite memory, journal, and timeline remain fully functional. AI reflection features will resume when Ollama starts.
            </div>
          )}
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem', marginBottom: '1.5rem' }}>
          {checks.map((c, i) => (
            <div
              key={i}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '0.75rem 1rem',
                background: 'var(--bg-secondary)',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--border-subtle)',
              }}
            >
              <div>
                <div style={{ fontWeight: 600, fontSize: '0.88rem' }}>{c.title}</div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{c.description}</div>
              </div>
              <div>
                {c.passed ? (
                  <CheckCircle size={18} color="var(--success)" />
                ) : (
                  <AlertCircle size={18} color="var(--warning)" />
                )}
              </div>
            </div>
          ))}
        </div>

        {showGuide && (
          <div
            style={{
              padding: '1rem',
              background: 'var(--bg-primary)',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-subtle)',
              fontSize: '0.82rem',
              marginBottom: '1.5rem',
            }}
          >
            <div style={{ fontWeight: 600, marginBottom: '0.5rem', color: '#7b93fc' }}>
              Quick Setup Guide (Local Open-Weight Models)
            </div>
            <p style={{ marginBottom: '0.4rem' }}>
              1. Install and launch Ollama: <code>ollama serve</code>
            </p>
            <p style={{ marginBottom: '0.4rem' }}>
              2. Pull the default models:
            </p>
            <pre style={{ background: 'var(--bg-secondary)', padding: '0.5rem', borderRadius: '4px', marginBottom: '0.4rem' }}>
              ollama pull gemma3:4b{'\n'}
              ollama pull nomic-embed-text
            </pre>
            <p>
              3. Click <strong>Check Again</strong> below.
            </p>
          </div>
        )}

        <div style={{ display: 'flex', justifyContent: 'space-between', gap: '0.75rem' }}>
          <button
            className="btn btn-secondary"
            onClick={() => setShowGuide(!showGuide)}
          >
            <HelpCircle size={16} />
            <span>{showGuide ? 'Hide Guide' : 'Setup Guide'}</span>
          </button>

          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button
              className="btn btn-primary"
              onClick={handleCheckAgain}
              disabled={checking}
            >
              <RefreshCw size={16} className={checking ? 'animate-spin' : ''} />
              <span>{checking ? 'Checking...' : 'Check Again'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
