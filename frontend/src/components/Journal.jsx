import { useState, useEffect, useCallback } from 'react'
import { api } from '../api'

const MOOD_LABELS = { 1: 'Rough', 2: 'Low', 3: 'Okay', 4: 'Good', 5: 'Great' }
const MOOD_COLORS = {
  1: '#ef4444',
  2: '#f97316',
  3: '#f59e0b',
  4: '#84cc16',
  5: '#22c55e',
}

function getMoodColor(mood) {
  return MOOD_COLORS[mood] || 'var(--muted)'
}

function getEntryText(entry) {
  // Guard against old CLI data that might use different field names
  return entry?.text || entry?.content || entry?.entry || ''
}

export default function Journal() {
  const [entries, setEntries] = useState([])
  const [todaysEntry, setTodaysEntry] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selected, setSelected] = useState(null)
  const [writeMode, setWriteMode] = useState(false)
  const [form, setForm] = useState({ text: '', mood: 3 })
  const [saving, setSaving] = useState(false)

  const today = new Date().toISOString().split('T')[0]

  const load = useCallback(async () => {
    setError(null)
    try {
      const [all, todayE] = await Promise.all([api.getJournal(), api.getTodaysJournal()])
      setEntries(Array.isArray(all) ? all : [])
      setTodaysEntry(todayE && todayE.id ? todayE : null)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  function openWrite() {
    if (todaysEntry) {
      setForm({ text: getEntryText(todaysEntry), mood: todaysEntry.mood || 3 })
      setSelected(todaysEntry)
    } else {
      setForm({ text: '', mood: 3 })
      setSelected(null)
    }
    setWriteMode(true)
  }

  async function handleSave(e) {
    e.preventDefault()
    if (!form.text.trim()) return
    setSaving(true)
    try {
      if (todaysEntry) {
        await api.updateJournal(todaysEntry.id, { text: form.text, mood: Number(form.mood) })
      } else {
        await api.createJournal({ text: form.text, mood: Number(form.mood) })
      }
      setWriteMode(false)
      setSelected(null)
      load()
    } catch (e) {
      alert(e.message)
    } finally {
      setSaving(false)
    }
  }

  async function handleDelete(id) {
    if (!confirm('Delete this journal entry?')) return
    try {
      await api.deleteJournal(id)
      if (selected?.id === id) setSelected(null)
      setWriteMode(false)
      load()
    } catch (e) {
      alert(e.message)
    }
  }

  if (loading) return <PageShell><LoadingState /></PageShell>

  if (error) return (
    <PageShell>
      <div style={s.errorBox}>
        <div style={s.errorTitle}>Could not load journal</div>
        <div style={s.errorMsg}>{error}</div>
        <button onClick={load} style={s.retryBtn}>Retry</button>
      </div>
    </PageShell>
  )

  const hasTodayEntry = !!todaysEntry

  return (
    <PageShell>
      <div style={s.header}>
        <div>
          <h1 style={s.pageTitle}>Journal</h1>
          <p style={s.subtitle}>{entries.length} entr{entries.length !== 1 ? 'ies' : 'y'}</p>
        </div>
        <button onClick={openWrite} style={s.primaryBtn}>
          {hasTodayEntry ? '✎ Edit Today' : '+ Write Today'}
        </button>
      </div>

      {/* Today's entry preview */}
      {hasTodayEntry && !writeMode && (
        <div style={s.todayBanner}>
          <div style={s.todayLabel}>TODAY — {today}</div>
          <div style={s.todayMood}>
            <span style={{ ...s.moodDot, backgroundColor: getMoodColor(todaysEntry.mood) }} />
            <span style={{ color: getMoodColor(todaysEntry.mood), fontWeight: 600 }}>
              {MOOD_LABELS[todaysEntry.mood] || 'No mood'}
            </span>
          </div>
          <p style={s.todayPreview}>
            {(() => {
              const txt = getEntryText(todaysEntry)
              return txt.length > 200 ? txt.slice(0, 200) + '…' : txt
            })()}
          </p>
        </div>
      )}

      {!hasTodayEntry && !writeMode && (
        <div style={s.writePrompt}>
          <span style={s.promptIcon}>▪</span>
          <span>You haven't written today yet. How's your day?</span>
          <button onClick={openWrite} style={s.promptBtn}>Write now →</button>
        </div>
      )}

      {/* Write / edit form */}
      {writeMode && (
        <form onSubmit={handleSave} style={s.writeForm}>
          <div style={s.writeHeader}>
            <span style={s.writeDate}>{today}</span>
            <button type="button" onClick={() => setWriteMode(false)} style={s.closeBtn}>✕ Close</button>
          </div>

          {/* Mood picker */}
          <div style={s.moodRow}>
            <span style={s.moodLabel}>How are you?</span>
            {[1, 2, 3, 4, 5].map(m => (
              <button
                key={m}
                type="button"
                onClick={() => setForm(f => ({ ...f, mood: m }))}
                style={{
                  ...s.moodBtn,
                  borderColor: form.mood === m ? getMoodColor(m) : 'var(--border)',
                  backgroundColor: form.mood === m ? `${getMoodColor(m)}22` : 'transparent',
                  color: form.mood === m ? getMoodColor(m) : 'var(--muted)',
                }}
              >
                {MOOD_LABELS[m]}
              </button>
            ))}
          </div>

          <textarea
            value={form.text}
            onChange={e => setForm(f => ({ ...f, text: e.target.value }))}
            placeholder="What happened today? What are you thinking about?"
            rows={8}
            style={s.textarea}
            autoFocus
          />

          <div style={s.writeActions}>
            {hasTodayEntry && (
              <button type="button" onClick={() => handleDelete(todaysEntry.id)} style={s.deleteBtn}>
                Delete entry
              </button>
            )}
            <button type="submit" disabled={saving || !form.text.trim()} style={s.primaryBtn}>
              {saving ? 'Saving...' : hasTodayEntry ? 'Update' : 'Save Entry'}
            </button>
          </div>
        </form>
      )}

      {/* Past entries grid */}
      {entries.length > 0 && (
        <>
          <div style={s.sectionHeader}>
            {entries.length} Past Entr{entries.length !== 1 ? 'ies' : 'y'}
          </div>
          <div style={s.entryGrid}>
            {entries.map(entry => {
              if (!entry || !entry.id) return null
              return (
                <EntryCard
                  key={entry.id}
                  entry={entry}
                  isToday={entry.date === today}
                  selected={selected?.id === entry.id}
                  onSelect={() => setSelected(prev => prev?.id === entry.id ? null : entry)}
                  onDelete={() => handleDelete(entry.id)}
                />
              )
            })}
          </div>
        </>
      )}

      {/* Read panel — slides in from bottom-right */}
      {selected && !writeMode && (
        <div style={s.readPanel}>
          <div style={s.readHeader}>
            <span style={s.readDate}>{selected.date}</span>
            <div style={s.readMood}>
              <span style={{ ...s.moodDot, backgroundColor: getMoodColor(selected.mood) }} />
              <span style={{ color: getMoodColor(selected.mood), fontSize: '0.75rem' }}>
                {MOOD_LABELS[selected.mood] || ''}
              </span>
            </div>
            <button onClick={() => setSelected(null)} style={s.closeBtn}>✕</button>
          </div>
          <p style={s.readBody}>{getEntryText(selected)}</p>
          <button
            onClick={() => handleDelete(selected.id)}
            style={{ ...s.deleteBtn, marginTop: 14 }}
          >
            Delete this entry
          </button>
        </div>
      )}
    </PageShell>
  )
}

function EntryCard({ entry, isToday, selected, onSelect, onDelete }) {
  const mood = entry.mood || 0
  const color = getMoodColor(mood)
  const text = getEntryText(entry)

  return (
    <div
      onClick={onSelect}
      style={{
        ...s.entryCard,
        borderColor: selected ? 'var(--amber)' : 'var(--border)',
        cursor: 'pointer',
      }}
    >
      <div style={s.entryTop}>
        <span style={s.entryDate}>{isToday ? 'Today' : entry.date}</span>
        {mood > 0 && (
          <>
            <span style={{ ...s.moodDot, backgroundColor: color, width: 7, height: 7 }} />
            <span style={{ fontSize: '0.68rem', color, fontFamily: "'JetBrains Mono', monospace" }}>
              {MOOD_LABELS[mood]}
            </span>
          </>
        )}
      </div>
      <p style={s.entryPreview}>
        {text.length > 120 ? text.slice(0, 120) + '…' : text || '(no content)'}
      </p>
    </div>
  )
}

function LoadingState() {
  return (
    <div style={{ display: 'flex', gap: 6, padding: 48 }}>
      {[0, 1, 2].map(i => (
        <span key={i} style={{
          width: 7, height: 7, borderRadius: '50%', backgroundColor: 'var(--amber)',
          display: 'inline-block',
          animation: 'pulse-dot 1.2s ease-in-out infinite',
          animationDelay: `${i * 160}ms`,
        }} />
      ))}
    </div>
  )
}

function PageShell({ children }) {
  return <div style={s.page}>{children}</div>
}

const s = {
  page: { padding: '32px 36px', maxWidth: 860, animation: 'fadeIn 0.2s ease' },
  header: { display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 24 },
  pageTitle: { fontSize: '1.8rem', fontWeight: 700, color: '#e6edf3', lineHeight: 1.1 },
  subtitle: { fontSize: '0.75rem', color: 'var(--muted)', fontFamily: "'JetBrains Mono', monospace", marginTop: 4 },
  primaryBtn: {
    backgroundColor: 'var(--amber)', color: '#0d1117', border: 'none',
    borderRadius: 6, padding: '8px 18px', fontWeight: 700, fontSize: '0.82rem',
    cursor: 'pointer', fontFamily: 'inherit',
  },
  errorBox: {
    padding: '32px', backgroundColor: 'var(--surface)', border: '1px solid var(--red)',
    borderRadius: 10, marginTop: 20,
  },
  errorTitle: { fontWeight: 700, color: 'var(--red)', marginBottom: 6, fontSize: '0.9rem' },
  errorMsg: { color: 'var(--muted)', fontFamily: "'JetBrains Mono', monospace", fontSize: '0.78rem', marginBottom: 16 },
  retryBtn: {
    background: 'none', border: '1px solid var(--red)', color: 'var(--red)',
    borderRadius: 6, padding: '6px 16px', cursor: 'pointer', fontFamily: 'inherit', fontSize: '0.78rem',
  },
  todayBanner: {
    backgroundColor: 'var(--surface)', border: '1px solid var(--amber)', borderRadius: 10,
    padding: '16px 20px', marginBottom: 24,
  },
  todayLabel: {
    fontSize: '0.65rem', fontFamily: "'JetBrains Mono', monospace",
    color: 'var(--amber)', letterSpacing: '0.08em', marginBottom: 6,
  },
  todayMood: { display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 },
  moodDot: { width: 10, height: 10, borderRadius: '50%', display: 'inline-block', flexShrink: 0 },
  todayPreview: { fontSize: '0.88rem', color: 'var(--text)', lineHeight: 1.6 },
  writePrompt: {
    display: 'flex', alignItems: 'center', gap: 12, padding: '16px 20px',
    backgroundColor: 'var(--surface)', border: '1px dashed var(--border)', borderRadius: 10,
    marginBottom: 24, fontSize: '0.85rem', color: 'var(--muted)',
  },
  promptIcon: { color: 'var(--amber)', fontSize: '1.1rem' },
  promptBtn: {
    marginLeft: 'auto', background: 'none', border: 'none', color: 'var(--amber)',
    cursor: 'pointer', fontSize: '0.82rem', fontFamily: 'inherit', fontWeight: 600,
  },
  writeForm: {
    backgroundColor: 'var(--surface)', border: '1px solid var(--amber)',
    borderRadius: 10, padding: '20px', marginBottom: 24,
  },
  writeHeader: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 },
  writeDate: { fontSize: '0.75rem', fontFamily: "'JetBrains Mono', monospace", color: 'var(--amber)' },
  closeBtn: {
    background: 'none', border: 'none', color: 'var(--muted)', cursor: 'pointer',
    fontSize: '0.78rem', fontFamily: "'JetBrains Mono', monospace",
  },
  moodRow: { display: 'flex', alignItems: 'center', gap: 6, marginBottom: 14, flexWrap: 'wrap' },
  moodLabel: {
    fontSize: '0.72rem', color: 'var(--muted)', fontFamily: "'JetBrains Mono', monospace", marginRight: 4,
  },
  moodBtn: {
    border: '1px solid', borderRadius: 20, padding: '3px 12px', fontSize: '0.75rem',
    cursor: 'pointer', fontFamily: 'inherit', transition: 'all 0.15s', background: 'none',
  },
  textarea: {
    width: '100%', backgroundColor: 'var(--bg)', border: '1px solid var(--border)',
    borderRadius: 8, padding: '14px 16px', color: 'var(--text)', fontFamily: 'inherit',
    fontSize: '0.9rem', lineHeight: 1.7, resize: 'vertical', outline: 'none',
    transition: 'border-color 0.15s', minHeight: 160,
  },
  writeActions: { marginTop: 14, display: 'flex', justifyContent: 'flex-end', gap: 10, alignItems: 'center' },
  deleteBtn: {
    background: 'none', border: 'none', color: 'var(--red)', cursor: 'pointer',
    fontSize: '0.78rem', fontFamily: 'inherit', marginRight: 'auto',
  },
  sectionHeader: {
    fontSize: '0.72rem', fontFamily: "'JetBrains Mono', monospace", color: 'var(--muted)',
    textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 12,
    paddingBottom: 8, borderBottom: '1px solid var(--border)',
  },
  entryGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 10 },
  entryCard: {
    backgroundColor: 'var(--surface)', border: '1px solid',
    borderRadius: 8, padding: '12px 14px', transition: 'border-color 0.15s',
  },
  entryTop: { display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 },
  entryDate: { fontSize: '0.72rem', fontFamily: "'JetBrains Mono', monospace", color: 'var(--muted)', flex: 1 },
  entryPreview: { fontSize: '0.8rem', color: 'var(--muted)', lineHeight: 1.5 },
  readPanel: {
    position: 'fixed', bottom: 24, right: 24, width: 420,
    maxWidth: 'calc(100vw - 48px)',
    backgroundColor: 'var(--surface)', border: '1px solid var(--amber)', borderRadius: 12,
    padding: '20px', boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
    maxHeight: '60vh', overflowY: 'auto', zIndex: 100,
  },
  readHeader: { display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 },
  readDate: { fontSize: '0.72rem', fontFamily: "'JetBrains Mono', monospace", color: 'var(--muted)', flex: 1 },
  readMood: { display: 'flex', alignItems: 'center', gap: 5 },
  readBody: { fontSize: '0.88rem', color: 'var(--text)', lineHeight: 1.7, whiteSpace: 'pre-wrap' },
  empty: { padding: '48px 0', color: 'var(--muted)', fontSize: '0.85rem', textAlign: 'center' },
}
