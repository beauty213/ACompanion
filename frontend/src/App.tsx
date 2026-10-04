import React, { useEffect, useState } from 'react'
import { api } from './api/client'
import {
  AIStatus,
  JournalEntry,
  Module,
} from './api/types'
import { DiagnosticsModal } from './components/DiagnosticsModal'
import { JournalExpressView } from './components/JournalExpressView'
import { Sidebar } from './components/Sidebar'
import { SettingsView } from './components/SettingsView'

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<string>('journal-express')
  const [aiStatus, setAiStatus] = useState<AIStatus | null>(null)
  const [isDiagnosticsOpen, setIsDiagnosticsOpen] = useState<boolean>(false)

  // Data state
  const [modules, setModules] = useState<Module[]>([])
  const [journal, setJournal] = useState<JournalEntry[]>([])

  const refreshData = async () => {
    try {
      const [j, mods, ai] = await Promise.allSettled([
        api.getJournal(),
        api.getModules(),
        api.getAIStatus(),
      ])

      if (j.status === 'fulfilled') setJournal(j.value)
      if (mods.status === 'fulfilled') setModules(mods.value)
      if (ai.status === 'fulfilled') setAiStatus(ai.value)
      else {
        setAiStatus({
          runtime: 'Ollama',
          runtime_available: false,
          model: 'gemma3:4b',
          model_available: false,
          embeddings_available: false,
          inference_test: false,
          ready: false,
          offline_capable: true,
          available_models: [],
        })
      }
    } catch (e) {
      console.error('Failed to load initial data:', e)
    }
  }

  useEffect(() => {
    refreshData()
  }, [])

  // Journal handlers
  const handleCreateJournal = async (title: string, content: string, moduleId?: string) => {
    await api.createJournal({ title, content, module_id: moduleId })
    await refreshData()
  }

  const handleDeleteJournal = async (id: string) => {
    await api.deleteJournal(id)
    await refreshData()
  }

  // Seed / Reset / Export
  const handleSeedData = async () => {
    await api.seedData()
    await refreshData()
  }

  const handleResetData = async () => {
    await api.resetData()
    await refreshData()
  }

  const handleExportData = async () => {
    const data = await api.exportData()
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: 'application/json',
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `anchor-export-${new Date().toISOString().slice(0, 10)}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="app-container">
      <Sidebar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        aiStatus={aiStatus}
        onOpenDiagnostics={() => setIsDiagnosticsOpen(true)}
      />

      <main className="main-content">
        {currentTab === 'journal-express' && (
          <JournalExpressView
            entries={journal}
            modules={modules}
            onCreateEntry={handleCreateJournal}
            onDeleteEntry={handleDeleteJournal}
          />
        )}

        {currentTab === 'settings' && (
          <SettingsView
            aiStatus={aiStatus}
            onOpenDiagnostics={() => setIsDiagnosticsOpen(true)}
            onSeedData={handleSeedData}
            onResetData={handleResetData}
            onExportData={handleExportData}
          />
        )}
      </main>

      <DiagnosticsModal
        isOpen={isDiagnosticsOpen}
        onClose={() => setIsDiagnosticsOpen(false)}
        aiStatus={aiStatus}
        onRefresh={async () => {
          try {
            const ai = await api.checkAI()
            setAiStatus(ai)
          } catch {
            await refreshData()
          }
        }}
      />
    </div>
  )
}
export default App
