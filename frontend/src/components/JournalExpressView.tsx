import React, { useEffect, useState } from 'react'
import {
  ExternalLink,
  Flame,
  Globe,
  Maximize2,
  RefreshCw,
  Search,
  Shuffle,
  Smile,
  Trash2,
  X,
  Zap,
} from 'lucide-react'
import { JournalEntry, MemeCritique, Module } from '../api/types'
import { api } from '../api/client'

interface JournalExpressViewProps {
  entries: JournalEntry[]
  modules?: Module[]
  onCreateEntry: (title: string, content: string, moduleId?: string) => Promise<void>
  onDeleteEntry: (id: string) => Promise<void>
}

interface OnlineMemeItem {
  id?: string
  meme_url: string
  verdict: string
  critique: string
  source_title?: string
  source_platform?: string
  source_url?: string
  query_used?: string
  category?: string
  collection_type?: string
}

export const JournalExpressView: React.FC<JournalExpressViewProps> = ({
  entries,
  modules = [],
  onCreateEntry,
  onDeleteEntry,
}) => {
  const [content, setContent] = useState('')
  const [title, setTitle] = useState('')
  const [selectedModuleId, setSelectedModuleId] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [search, setSearch] = useState('')
  const [selectedMeme, setSelectedMeme] = useState<OnlineMemeItem | null>(null)
  const [showExplorer, setShowExplorer] = useState(false)
  const [explorerMemes, setExplorerMemes] = useState<OnlineMemeItem[]>([])
  const [explorerSearch, setExplorerSearch] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [isSearchingExplorer, setIsSearchingExplorer] = useState(false)
  const [overrides, setOverrides] = useState<Record<string, MemeCritique>>({})

  // Load online memes for explorer modal
  useEffect(() => {
    const loadMemes = async () => {
      try {
        const res = await api.getMemes()
        if (res && res.memes) {
          setExplorerMemes(res.memes)
        }
      } catch (err) {
        console.error('Failed to load explorer memes:', err)
      }
    }
    loadMemes()
  }, [])

  const handleSearchExplorer = async (query: string) => {
    setExplorerSearch(query)
    if (!query.trim()) {
      const res = await api.getMemes()
      if (res && res.memes) setExplorerMemes(res.memes)
      return
    }
    setIsSearchingExplorer(true)
    try {
      const res = await api.searchMemes(query)
      if (res && res.results) {
        setExplorerMemes(res.results)
      }
    } catch (err) {
      console.error('Failed to search online memes:', err)
    } finally {
      setIsSearchingExplorer(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!content.trim() || isSubmitting) return

    setIsSubmitting(true)
    try {
      await onCreateEntry(title.trim(), content.trim(), selectedModuleId || undefined)
      setContent('')
      setTitle('')
      setSelectedModuleId('')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleShuffleMeme = async (entryId: string, entryContent: string, currentMeme?: string) => {
    try {
      const res = await api.getCritique({
        text: entryContent,
        current_meme: currentMeme,
        shuffle: true,
        entry_id: entryId,
      })
      if (res) {
        setOverrides((prev) => ({
          ...prev,
          [entryId]: res,
        }))
      }
    } catch (err) {
      console.error('Failed to shuffle critique:', err)
    }
  }

  const filteredEntries = entries.filter((entry) => {
    if (!search.trim()) return true
    const q = search.toLowerCase()
    return (
      (entry.title && entry.title.toLowerCase().includes(q)) ||
      entry.content.toLowerCase().includes(q)
    )
  })

  const getVerdictColor = (verdict: string) => {
    const v = verdict.toUpperCase()
    if (v.includes('CLOWN') || v.includes('CHAOS') || v.includes('BAD')) return '#ef4444' // red
    if (v.includes('NOSTALGIA') || v.includes('DISAPPOINTED') || v.includes('TRUTH')) return '#f59e0b' // amber
    if (v.includes('OVERTHINKING') || v.includes('THINK') || v.includes('PARALYSIS')) return '#3b82f6' // blue
    if (v.includes('SNAKE') || v.includes('STAND') || v.includes('REALITY')) return '#10b981' // green
    return '#8b5cf6' // purple
  }

  const getPlatformBadge = (platform?: string) => {
    const p = (platform || '').toLowerCase()
    if (p.includes('reddit')) {
      return { label: '🔴 Reddit (r/memes)', bg: 'rgba(255, 69, 0, 0.15)', color: '#ff4500' }
    }
    if (p.includes('twitter') || p.includes('x')) {
      return { label: '🐦 Twitter / X', bg: 'rgba(29, 161, 242, 0.15)', color: '#38bdf8' }
    }
    if (p.includes('instagram')) {
      return { label: '📸 Instagram', bg: 'rgba(225, 48, 108, 0.15)', color: '#f43f5e' }
    }
    if (p.includes('google')) {
      return { label: '🌐 Google Images', bg: 'rgba(66, 133, 244, 0.15)', color: '#60a5fa' }
    }
    if (p.includes('know your meme') || p.includes('kym')) {
      return { label: '🧠 Know Your Meme', bg: 'rgba(168, 85, 247, 0.15)', color: '#c084fc' }
    }
    return { label: '🌐 Social Media / Web', bg: 'rgba(255, 255, 255, 0.1)', color: '#e2e8f0' }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', maxWidth: '1100px', margin: '0 auto', width: '100%' }}>
      {/* App Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
            <div style={{ padding: '0.45rem', background: 'rgba(139, 92, 246, 0.12)', borderRadius: '12px' }}>
              <Flame size={26} color="var(--accent)" />
            </div>
            <h1 style={{ fontSize: '2.1rem', fontWeight: 800, margin: 0, letterSpacing: '-0.03em', color: 'var(--text-primary)' }}>
              wts on my mind today
            </h1>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.94rem', margin: '0.4rem 0 0 0' }}>
            Express raw thoughts. Get immediately reality-checked by trending memes, SpongeBob, Anime, Hollywood & Tollywood roasts.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => setShowExplorer(true)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.45rem',
              borderRadius: '20px',
              padding: '0.55rem 1.15rem',
              border: '1.5px solid var(--border-subtle)',
              background: '#ffffff',
              boxShadow: '0 2px 10px rgba(139, 92, 246, 0.08)',
              fontWeight: 600,
            }}
          >
            <Globe size={16} color="var(--accent)" />
            <span>Google & Social Memes ({explorerMemes.length || 'Live'})</span>
          </button>
        </div>
      </div>

      {/* Express Composer Card */}
      <div
        className="card"
        style={{
          padding: '1.75rem',
          border: '1.5px solid var(--border-focus)',
          background: '#ffffff',
          borderRadius: '18px',
          boxShadow: '0 8px 30px rgba(139, 92, 246, 0.08)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
          <Zap size={20} color="var(--accent)" />
          <h3 style={{ fontSize: '1.25rem', fontWeight: 800, margin: 0, color: 'var(--text-primary)' }}>
            type here something
          </h3>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginLeft: 'auto' }}>
            Write freely — real memes will roast the situation
          </span>
        </div>

        {/* Monkey Thinking Hero Banner */}
        <div className="monkey-thinking-card">
          <img
            src="/memes/meme10.jpg"
            alt="Monkey Thinking Meme"
            className="monkey-thinking-img"
          />
          <div className="monkey-thinking-text">
            <div className="monkey-thinking-title">
              <span>🐵 Monkey Thinking Moment</span>
            </div>
            <div className="monkey-thinking-sub">
              Sitting with your finger on your chin contemplating poor life choices? Type whatever is spiraling in your head today.
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
            <input
              className="input"
              style={{ flex: 2, minWidth: '220px' }}
              placeholder="Situation or dilemma title (optional)..."
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
            {modules.length > 0 && (
              <select
                className="input"
                style={{ flex: 1, minWidth: '180px' }}
                value={selectedModuleId}
                onChange={(e) => setSelectedModuleId(e.target.value)}
              >
                <option value="">👤 Tag: General (No person)</option>
                {modules.map((m) => (
                  <option key={m.id} value={m.id}>
                    👤 Tag: {m.alias || m.name}
                  </option>
                ))}
              </select>
            )}
          </div>

          <textarea
            className="textarea"
            rows={4}
            placeholder="type here something..."
            value={content}
            onChange={(e) => setContent(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                e.preventDefault()
                handleSubmit(e)
              }
            }}
            required
            style={{ fontSize: '0.96rem', lineHeight: 1.6 }}
          />

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)', fontSize: '0.82rem' }}>
              <Globe size={16} color="var(--accent)" />
              <span>Memes sourced from SpongeBob, Anime, Hollywood, Tollywood, and Socials.</span>
            </div>

            {/* Thinking Button with Green Snake Judging beside it */}
            <div className="thinking-action-wrapper">
              <button
                type="submit"
                className="btn btn-primary"
                disabled={isSubmitting || !content.trim()}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  padding: '0.65rem 1.6rem',
                  fontSize: '0.95rem',
                  fontWeight: 700,
                  borderRadius: '9999px',
                }}
              >
                <Zap size={16} />
                <span>{isSubmitting ? 'thinking...' : 'thinking'}</span>
              </button>

              <div className="snake-judging-side" title="Green snake is watching and judging your thoughts">
                <img
                  src="/memes/meme7.jpg"
                  alt="Green snake judging"
                  className="snake-judging-avatar"
                />
                <div>
                  <div className="snake-judging-caption">🐍 green snake judging</div>
                  <div className="snake-judging-hint">judging every word</div>
                </div>
              </div>
            </div>
          </div>
        </form>
      </div>

      {/* Stream Controls */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0 }}>
            Expressions & Meme Roasts ({filteredEntries.length})
          </h2>
        </div>

        <div style={{ position: 'relative', minWidth: '240px' }}>
          <Search size={15} style={{ position: 'absolute', left: '10px', top: '10px', color: 'var(--text-muted)' }} />
          <input
            className="input"
            style={{ paddingLeft: '2rem', fontSize: '0.82rem' }}
            placeholder="Search past expressions..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      {/* Expressions Feed */}
      {filteredEntries.length === 0 ? (
        <div
          className="card"
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '3.5rem 1.5rem',
            textAlign: 'center',
            gap: '1rem',
            border: '2px dashed var(--border-subtle)',
            borderRadius: '16px',
          }}
        >
          <div style={{ padding: '1rem', background: 'rgba(56, 189, 248, 0.1)', borderRadius: '50%' }}>
            <Globe size={36} color="#38bdf8" />
          </div>
          <div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, margin: '0 0 0.4rem 0' }}>
              No expressions logged yet
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', maxWidth: '440px', margin: 0 }}>
              Write your raw thoughts above. Google & social media memes will give you an immediate reality-check critique.
            </p>
          </div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {filteredEntries.map((entry) => {
            const rawCritique = overrides[entry.id] || entry.critique
            const critique: MemeCritique = rawCritique || {
              meme_url: 'https://i.imgflip.com/24y43o.jpg',
              verdict: 'UNDISPUTED REALITY',
              critique: 'Actions reveal commitment; words just reveal intentions. Believe what they consistently do, not what they tell you in the moment.',
              source_platform: 'Google Images',
              source_title: 'Change My Mind Meme',
              source_url: 'https://knowyourmeme.com/memes/steven-crowders-change-my-mind-mug',
              query_used: 'change my mind reality check meme google',
            }

            const verdictColor = getVerdictColor(critique.verdict)
            const entryMod = modules.find((m) => m.id === entry.module_id)
            const platformBadge = getPlatformBadge(critique.source_platform)
            const memeUrl = critique.meme_url || critique.meme_file || 'https://i.imgflip.com/24y43o.jpg'

            return (
              <div
                key={entry.id}
                className="card"
                style={{
                  padding: '1.25rem',
                  display: 'flex',
                  gap: '1.5rem',
                  alignItems: 'stretch',
                  flexWrap: 'wrap',
                  borderRadius: '14px',
                  border: '1px solid var(--border-subtle)',
                  background: 'var(--bg-secondary)',
                }}
              >
                {/* Left Side: User Expression */}
                <div style={{ flex: 3, minWidth: '300px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.5rem', flexWrap: 'wrap' }}>
                      <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                        {new Date(entry.created_at).toLocaleDateString(undefined, {
                          weekday: 'short',
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </span>
                      {entryMod && (
                        <span className="badge badge-secondary" style={{ fontSize: '0.72rem' }}>
                          👤 {entryMod.alias || entryMod.name}
                        </span>
                      )}
                    </div>

                    {entry.title && (
                      <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.45rem', color: 'var(--text-primary)' }}>
                        {entry.title}
                      </h3>
                    )}

                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.94rem', whiteSpace: 'pre-line', lineHeight: 1.6, margin: 0 }}>
                      "{entry.content}"
                    </p>
                  </div>

                  <div style={{ marginTop: '1rem', paddingTop: '0.75rem', borderTop: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      Local SQLite storage
                    </span>
                    <button
                      className="btn btn-ghost btn-sm"
                      onClick={() => onDeleteEntry(entry.id)}
                      title="Delete entry"
                      style={{ color: 'var(--text-muted)' }}
                    >
                      <Trash2 size={15} />
                    </button>
                  </div>
                </div>

                {/* Right Side: Online Meme Critique Card */}
                <div
                  style={{
                    flex: 2,
                    minWidth: '270px',
                    background: 'var(--bg-primary)',
                    borderRadius: '12px',
                    padding: '1rem',
                    border: `1px solid ${verdictColor}40`,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.75rem',
                    boxShadow: '0 4px 14px rgba(0,0,0,0.2)',
                  }}
                >
                  {/* Verdict & Platform Header */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.4rem' }}>
                    <div
                      style={{
                        fontSize: '0.75rem',
                        fontWeight: 800,
                        color: verdictColor,
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em',
                        background: `${verdictColor}18`,
                        padding: '0.2rem 0.6rem',
                        borderRadius: '6px',
                      }}
                    >
                      {critique.verdict}
                    </div>

                    <div style={{ display: 'flex', gap: '0.35rem' }}>
                      <button
                        className="btn btn-ghost btn-sm"
                        onClick={() => handleShuffleMeme(entry.id, entry.content, memeUrl)}
                        title="Shuffle reaction from Google/Social"
                        style={{ padding: '4px', fontSize: '0.72rem', display: 'flex', alignItems: 'center', gap: '3px' }}
                      >
                        <Shuffle size={13} />
                        <span>Shuffle</span>
                      </button>
                    </div>
                  </div>

                  {/* Matched Situation Tag */}
                  {critique.situation && (
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', fontWeight: 600 }}>
                      📌 {critique.situation}
                    </div>
                  )}

                  {/* Platform Origin Tag */}
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.72rem' }}>
                    <span
                      style={{
                        background: platformBadge.bg,
                        color: platformBadge.color,
                        padding: '2px 8px',
                        borderRadius: '12px',
                        fontWeight: 600,
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px',
                      }}
                    >
                      {platformBadge.label}
                    </span>

                    {critique.source_url && (
                      <a
                        href={critique.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          color: 'var(--text-muted)',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '3px',
                          textDecoration: 'none',
                        }}
                        title="View original on web"
                      >
                        <span>Source</span>
                        <ExternalLink size={11} />
                      </a>
                    )}
                  </div>

                  {/* Online Meme Image Frame */}
                  <div
                    onClick={() => setSelectedMeme({
                      meme_url: memeUrl,
                      verdict: critique.verdict,
                      critique: critique.critique,
                      source_title: critique.source_title,
                      source_platform: critique.source_platform,
                      source_url: critique.source_url,
                      query_used: critique.query_used,
                    })}
                    style={{
                      width: '100%',
                      maxHeight: '190px',
                      borderRadius: '8px',
                      overflow: 'hidden',
                      background: '#0a0a0a',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      cursor: 'pointer',
                      border: '1px solid var(--border-subtle)',
                      position: 'relative',
                    }}
                  >
                    <img
                      src={memeUrl}
                      alt={critique.verdict}
                      onError={(e) => {
                        // Fallback image if remote host is blocked
                        ;(e.currentTarget as HTMLImageElement).src = 'https://i.imgflip.com/24y43o.jpg'
                      }}
                      style={{ width: '100%', height: '100%', maxHeight: '190px', objectFit: 'contain', display: 'block' }}
                    />
                    <div
                      style={{
                        position: 'absolute',
                        bottom: '6px',
                        right: '6px',
                        background: 'rgba(0,0,0,0.75)',
                        padding: '3px 6px',
                        borderRadius: '4px',
                        color: '#fff',
                        fontSize: '0.7rem',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '3px',
                      }}
                    >
                      <Maximize2 size={11} />
                      <span>Zoom</span>
                    </div>
                  </div>

                  {/* Roast Critique Text */}
                  <p
                    style={{
                      fontSize: '0.85rem',
                      color: 'var(--text-primary)',
                      lineHeight: 1.45,
                      margin: 0,
                      fontWeight: 500,
                      borderLeft: `3px solid ${verdictColor}`,
                      paddingLeft: '0.65rem',
                    }}
                  >
                    {critique.critique}
                  </p>

                  {/* Query Used Footnote */}
                  {critique.query_used && (
                    <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>
                      Search: <em>"{critique.query_used}"</em>
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Google & Social Media Meme Explorer Modal */}
      {showExplorer && (() => {
        // Deduplicate memes by meme_url to eliminate any repeating identical memes
        const uniqueMemes = Array.from(
          new Map(explorerMemes.map((m) => [m.meme_url, m])).values()
        )

        const categories = [
          { id: 'all', label: `All Memes (${uniqueMemes.length})` },
          { id: 'my_collection', label: '📁 My Collection' },
          { id: 'trending', label: '🔥 Trending' },
          { id: 'spongebob', label: '🧽 SpongeBob' },
          { id: 'anime', label: '🍙 Anime' },
          { id: 'hollywood', label: '🎬 Hollywood' },
          { id: 'tollywood', label: '🎭 Tollywood' },
        ]

        const displayedMemes = uniqueMemes.filter((m) => {
          if (selectedCategory === 'all') return true
          const cat = (m.category || m.collection_type || '').toLowerCase()
          const platform = (m.source_platform || '').toLowerCase()
          const title = (m.source_title || '').toLowerCase()
          const sit = (m.query_used || m.verdict || '').toLowerCase()

          if (selectedCategory === 'my_collection') {
            return cat === 'my_collection' || m.meme_url.startsWith('/memes/')
          }
          if (selectedCategory === 'trending') {
            return cat === 'trending' || platform.includes('tiktok') || sit.includes('trending')
          }
          if (selectedCategory === 'spongebob') {
            return cat === 'spongebob' || platform.includes('spongebob') || title.includes('spongebob')
          }
          if (selectedCategory === 'anime') {
            return cat === 'anime' || platform.includes('anime') || title.includes('naruto') || title.includes('jojo') || title.includes('death note')
          }
          if (selectedCategory === 'hollywood') {
            return cat === 'hollywood' || platform.includes('hollywood') || title.includes('dicaprio') || title.includes('bateman') || title.includes('godfather')
          }
          if (selectedCategory === 'tollywood') {
            return cat === 'tollywood' || platform.includes('tollywood') || title.includes('brahmanandam') || title.includes('pushpa') || title.includes('kishore')
          }
          return cat === selectedCategory
        })

        return (
          <div className="modal-overlay" onClick={() => setShowExplorer(false)}>
            <div
              className="modal-content"
              onClick={(e) => e.stopPropagation()}
              style={{
                maxWidth: '980px',
                maxHeight: '88vh',
                overflowY: 'auto',
                background: '#ffffff',
                borderRadius: '20px',
                border: '1.5px solid var(--border-subtle)',
                boxShadow: '0 20px 50px rgba(139, 92, 246, 0.15)',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.8rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                  <Globe size={24} color="var(--accent)" />
                  <h3 style={{ fontSize: '1.35rem', fontWeight: 800, margin: 0, color: 'var(--text-primary)' }}>
                    Google & Social Media Meme Explorer
                  </h3>
                </div>
                <button className="btn btn-ghost btn-sm" onClick={() => setShowExplorer(false)}>
                  <X size={20} />
                </button>
              </div>

              <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', marginBottom: '1.2rem' }}>
                Explore diverse, situation-specific memes: SpongeBob, Anime, Hollywood cinema, Tollywood pop culture, trending internet, and your personal meme collection.
              </p>

              {/* Category Filter Pills */}
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1.25rem' }}>
                {categories.map((c) => (
                  <button
                    key={c.id}
                    className={`pastel-pill ${selectedCategory === c.id ? 'active' : ''}`}
                    onClick={() => setSelectedCategory(c.id)}
                  >
                    {c.label}
                  </button>
                ))}
              </div>

              {/* Explorer Search Input */}
              <div style={{ position: 'relative', marginBottom: '1.25rem' }}>
                <Search size={16} style={{ position: 'absolute', left: '12px', top: '12px', color: 'var(--text-muted)' }} />
                <input
                  className="input"
                  style={{ paddingLeft: '2.4rem', fontSize: '0.9rem' }}
                  placeholder="Search memes by keyword (e.g. spongebob, anime, tollywood, money, overthinking)..."
                  value={explorerSearch}
                  onChange={(e) => handleSearchExplorer(e.target.value)}
                />
              </div>

              {displayedMemes.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-muted)' }}>
                  No memes found in this category. Try switching filters or search terms!
                </div>
              ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(210px, 1fr))', gap: '1rem' }}>
                  {displayedMemes.map((m, idx) => {
                    const badge = getPlatformBadge(m.source_platform)
                    return (
                      <div
                        key={m.id || idx}
                        onClick={() => setSelectedMeme(m)}
                        style={{
                          background: '#faf9fe',
                          borderRadius: '12px',
                          overflow: 'hidden',
                          border: '1.5px solid var(--border-subtle)',
                          cursor: 'pointer',
                          display: 'flex',
                          flexDirection: 'column',
                          padding: '10px',
                          gap: '8px',
                          boxShadow: '0 2px 8px rgba(139, 92, 246, 0.04)',
                          transition: 'transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease',
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.transform = 'translateY(-2px)'
                          e.currentTarget.style.boxShadow = '0 6px 18px rgba(139, 92, 246, 0.12)'
                          e.currentTarget.style.borderColor = 'var(--accent)'
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.transform = 'none'
                          e.currentTarget.style.boxShadow = '0 2px 8px rgba(139, 92, 246, 0.04)'
                          e.currentTarget.style.borderColor = 'var(--border-subtle)'
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span
                            style={{
                              fontSize: '0.68rem',
                              padding: '2px 8px',
                              borderRadius: '8px',
                              background: badge.bg,
                              color: badge.color,
                              fontWeight: 700,
                            }}
                          >
                            {badge.label}
                          </span>
                        </div>

                        <img
                          src={m.meme_url}
                          alt={m.verdict}
                          style={{
                            width: '100%',
                            height: '140px',
                            objectFit: 'contain',
                            background: '#ffffff',
                            borderRadius: '8px',
                            border: '1px solid var(--border-subtle)',
                          }}
                          loading="lazy"
                          onError={(e) => {
                            ;(e.currentTarget as HTMLImageElement).src = '/memes/meme10.jpg'
                          }}
                        />

                        <div style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--text-primary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                          {m.verdict}
                        </div>

                        {m.source_title && (
                          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                            {m.source_title}
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          </div>
        )
      })()}

      {/* Lightbox Image Preview Modal */}
      {selectedMeme && (
        <div
          className="modal-overlay"
          onClick={() => setSelectedMeme(null)}
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(30, 25, 50, 0.75)',
            backdropFilter: 'blur(6px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: '1.5rem',
          }}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              position: 'relative',
              maxWidth: '90vw',
              maxHeight: '90vh',
              background: '#ffffff',
              borderRadius: '20px',
              padding: '1.5rem',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              boxShadow: '0 25px 60px rgba(90, 70, 140, 0.25)',
              border: '1.5px solid var(--border-subtle)',
              gap: '1rem',
            }}
          >
            <div style={{ width: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <span style={{ fontWeight: 800, fontSize: '1.1rem', color: 'var(--text-primary)' }}>{selectedMeme.verdict}</span>
                {selectedMeme.source_platform && (
                  <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginLeft: '0.6rem', fontWeight: 600 }}>
                    ({selectedMeme.source_platform})
                  </span>
                )}
              </div>
              <button className="btn btn-ghost btn-sm" onClick={() => setSelectedMeme(null)}>
                <X size={20} />
              </button>
            </div>

            <img
              src={selectedMeme.meme_url}
              alt={selectedMeme.verdict}
              style={{ maxWidth: '85vw', maxHeight: '65vh', objectFit: 'contain', borderRadius: '12px', display: 'block' }}
            />

            {selectedMeme.critique && (
              <p style={{ fontSize: '0.92rem', color: 'var(--text-secondary)', margin: 0, maxWidth: '620px', textAlign: 'center', lineHeight: 1.5 }}>
                "{selectedMeme.critique}"
              </p>
            )}

            {selectedMeme.source_url && (
              <a
                href={selectedMeme.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-secondary btn-sm"
                style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', borderRadius: '20px', padding: '0.45rem 1rem' }}
              >
                <span>Open Source on {selectedMeme.source_platform || 'Web'}</span>
                <ExternalLink size={14} />
              </a>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
