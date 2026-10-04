export type MemoryType =
  | 'Experience'
  | 'Reflection'
  | 'Boundary'
  | 'Goal'
  | 'Commitment'
  | 'Event'
  | 'Value'
  | 'Pattern'
  | 'Person'
  | 'FutureSelfMessage'

export type MemoryStatus = 'ai_suggested' | 'user_confirmed' | 'user_edited'
export type ImportanceLevel = 'low' | 'med' | 'high'

export interface MemorySource {
  id: string
  memory_id: string
  source_type: string
  source_id: string
  excerpt?: string
  created_at: string
}

export interface Memory {
  id: string
  type: MemoryType
  title?: string
  content: string
  summary?: string
  related_people: string[]
  related_topics: string[]
  emotion?: string
  importance: ImportanceLevel
  confidence: number
  status: MemoryStatus
  source_journal_id?: string
  source_conversation_id?: string
  module_id?: string
  created_at: string
  updated_at: string
  confirmed_at?: string
  sources: MemorySource[]
}

export interface MemeCritique {
  meme_url: string
  verdict: string
  critique: string
  source_url?: string
  source_title?: string
  source_platform?: string
  query_used?: string
  situation?: string
  meme_file?: string
}

export interface JournalEntry {
  id: string
  title?: string
  content: string
  module_id?: string
  created_at: string
  updated_at: string
  suggested_memories?: Memory[]
  related_memories?: Memory[]
  critique?: MemeCritique
}

export interface Module {
  id: string
  name: string
  alias?: string
  relationship?: string
  description?: string
  created_at: string
  updated_at: string
  incident_count: number
  latest_incident_date?: string
  active_boundaries_count: number
}

export interface ModuleCreate {
  name: string
  alias?: string
  relationship?: string
  description?: string
}

export interface IncidentAnalysisReport {
  module_id: string
  module_name: string
  relationship?: string
  incident_count: number
  timeline_summary: string
  escalation_analysis: string
  documented_contradictions: string[]
  reciprocity_assessment: string
  active_boundaries: string[]
  clarifying_questions: string[]
  key_takeaway: string
  generated_at: string
}

export interface TimelineEvent {
  id: string
  item_type: 'journal' | 'memory'
  memory_type?: MemoryType
  title: string
  snippet: string
  importance?: ImportanceLevel
  module_id?: string
  module_name?: string
  module_alias?: string
  created_at: string
  date: string
  month: string
}

export interface TimelineMonthGroup {
  month: string
  events: TimelineEvent[]
}

export interface FutureSelfMessage {
  id: string
  message: string
  related_person?: string
  related_topic?: string
  importance: ImportanceLevel
  trigger_context: string
  expires_at?: string
  created_at: string
  triggered_at?: string
  dismissed: boolean
}

export interface Pattern {
  id: string
  title: string
  description: string
  memory_ids: string[]
  dismissed: boolean
  created_at: string
}

export interface AIStatus {
  runtime: string
  runtime_available: boolean
  model: string
  model_available: boolean
  embeddings_available: boolean
  inference_test: boolean
  ready: boolean
  offline_capable: boolean
  error_message?: string
  available_models: string[]
}

export interface ReflectionResponse {
  answer: string
  sources: string[]
  source_details: any[]
  reflective_question?: string
  status: string
  why_seeing_this?: string
}
