import {
  AIStatus,
  FutureSelfMessage,
  IncidentAnalysisReport,
  JournalEntry,
  MemeCritique,
  Memory,
  MemoryStatus,
  MemoryType,
  Module,
  ModuleCreate,
  Pattern,
  ReflectionResponse,
  TimelineMonthGroup,
} from './types'

const API_BASE = '/api'

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options?.headers || {}),
    },
  })
  if (!res.ok) {
    const errorText = await res.text()
    throw new Error(`API error (${res.status}): ${errorText || res.statusText}`)
  }
  return res.json()
}

export const api = {
  // Health
  checkHealth: () => request<{ status: string; app: string; version: string }>('/health'),

  // Modules / People Tracks
  getModules: () => request<Module[]>('/modules'),
  createModule: (data: ModuleCreate) =>
    request<Module>('/modules', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  deleteModule: (id: string) =>
    request<{ success: boolean; id: string }>(`/modules/${id}`, {
      method: 'DELETE',
    }),
  getModuleIncidents: (moduleId: string) =>
    request<JournalEntry[]>(`/modules/${moduleId}/incidents`),
  createModuleIncident: (moduleId: string, data: { title?: string; content: string }) =>
    request<JournalEntry>(`/modules/${moduleId}/incidents`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  analyzeModule: (moduleId: string) =>
    request<IncidentAnalysisReport>(`/modules/${moduleId}/analyze`, {
      method: 'POST',
    }),

  // Journal
  getJournal: (moduleId?: string) =>
    request<JournalEntry[]>(`/journal${moduleId ? `?module_id=${moduleId}` : ''}`),
  getJournalEntry: (id: string) => request<JournalEntry>(`/journal/${id}`),
  createJournal: (data: { title?: string; content: string; module_id?: string }) =>
    request<JournalEntry>('/journal', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  updateJournal: (id: string, data: { title?: string; content?: string; module_id?: string }) =>
    request<JournalEntry>(`/journal/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  deleteJournal: (id: string) =>
    request<{ success: boolean; id: string }>(`/journal/${id}`, {
      method: 'DELETE',
    }),
  getCritique: (data: { text: string; title?: string; current_meme?: string; shuffle?: boolean; entry_id?: string }) =>
    request<MemeCritique>('/critique', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Memories
  getMemories: (params?: {
    type?: MemoryType
    status?: MemoryStatus
    search?: string
    include_suggested?: boolean
  }) => {
    const query = new URLSearchParams()
    if (params?.type) query.set('type', params.type)
    if (params?.status) query.set('status', params.status)
    if (params?.search) query.set('search', params.search)
    if (params?.include_suggested !== undefined) {
      query.set('include_suggested', String(params.include_suggested))
    }
    const qs = query.toString()
    return request<Memory[]>(`/memories${qs ? `?${qs}` : ''}`)
  },
  getMemory: (id: string) => request<Memory>(`/memories/${id}`),
  createMemory: (data: Partial<Memory>) =>
    request<Memory>('/memories', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  updateMemory: (id: string, data: Partial<Memory>) =>
    request<Memory>(`/memories/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
  deleteMemory: (id: string) =>
    request<{ success: boolean; id: string }>(`/memories/${id}`, {
      method: 'DELETE',
    }),

  // Timeline
  getTimeline: (moduleId?: string) =>
    request<{ timeline: TimelineMonthGroup[]; total_events: number }>(
      `/timeline${moduleId ? `?module_id=${moduleId}` : ''}`
    ),

  // Future Self
  getFutureSelf: () => request<FutureSelfMessage[]>('/future-self'),
  createFutureSelf: (data: Partial<FutureSelfMessage>) =>
    request<FutureSelfMessage>('/future-self', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  dismissFutureSelf: (id: string) =>
    request<{ success: boolean; id: string }>(`/future-self/${id}/dismiss`, {
      method: 'PATCH',
    }),

  // Patterns
  getPatterns: () => request<Pattern[]>('/patterns'),
  detectPatterns: () => request<{ detected: boolean; patterns: Pattern[]; message: string }>('/patterns/detect', { method: 'POST' }),
  dismissPattern: (id: string) =>
    request<{ success: boolean; id: string }>(`/patterns/${id}/dismiss`, {
      method: 'PATCH',
    }),

  // AI & Reflection
  getAIStatus: () => request<AIStatus>('/ai/status'),
  checkAI: () => request<AIStatus>('/ai/check', { method: 'POST' }),
  askPast: (data: { query: string; top_k?: number; filter_person?: string }) =>
    request<ReflectionResponse>('/ask-past', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Seed / Reset / Export
  seedData: () => request<any>('/seed', { method: 'POST' }),
  resetData: () => request<any>('/reset', { method: 'POST' }),
  exportData: () => request<any>('/export'),
  getMemes: () => request<{ memes: any[] }>('/memes'),
  searchMemes: (q: string) =>
    request<{ query: string; results: any[] }>(
      `/memes/search?q=${encodeURIComponent(q)}`
    ),
}

