import { useState, useEffect, useCallback } from 'react'
import { api } from '../api'

const MOOD_LABELS = { 1: 'Rough', 2: 'Low', 3: 'Okay', 4: 'Good', 5: 'Great' }
const MOOD_COLORS = {
  1: 'var(--red)',
  2: '#f97316',
  3: 'var(--amber)',
  4: '#84cc16',
  5: 'var(--green)',
}

export default function Journal() {
  const [entries, setEntries] = useState([])
  const [todaysEntry, setTodaysEntry] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState(null)   // entry being read/edited
  const [writeMode, setWriteMode] = useState(false)
  const [form, setForm] = useState({ text: '', mood: 3 })
  const [saving, setSaving] = useState(false)

  const today = new Date().toISOString().split('T')[0]

  const load = useCallback(async () => {
    try {
      const [all, todayE] = await Promise.all([api.getJournal(), api.getTodaysJournal()])
      setEntries(all)
      setTodaysEntry(todayE?.id ? todayE : null)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  function openWrite() {
    if (todaysEntry) {
      // Edit mode — load today's existing entry
      setForm({ text: todaysEntry.text, mood: todaysEntry.mood || 3 })
      setSelected(todaysEntry)
    } else {
      setForm({ text: '', mood: 3 })
      setSelected(null)
    }
    setWriteMode(true)
  }

  async function handleSave(e) {
    e.preventDefault()
    setSaving(true)
    try {
      if (todaysEntry) {
        await api.updateJournal(todaysEntry.id, { text: form.text, mood: form.mood })
      } else {
        await api.createJournal({ text: form.text, mood: form.mood })
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
    await api.deleteJournal(id)
    if (selected?.id === id) setSelected(null)
    setWriteMode(false)
    load()
  }

  if (loading) return <PageShell><div style={s.empty}>Loading...</div></PageShell>

  const hasTodayEntry = !!todaysEntry

  return (
    <PageShell>
      <div style={s.header}>
        <div>
          <h1 style={s.pageTitle}>Journal</h1>
          <p style={s.subtitle}>{entries.length} entries</p>
        </div>
        <button onClick={openWrite} style={s.primaryBtn}>
          {hasTodayEntry ? '✎ Edit Today' : '+ Write Today'}
        </button>
      </div>

      {/* Today's banner */}
      {hasTodayEntry && !writeMode && (
        <div style={s.todayBanner}>
          <div style={s.todayLabel}>TODAY — {today}</div>
          <div style={s.todayMood}>
            <span style={{ ...s.moodDot, backgroundColor: MOOD_COLORS[todaysEntry.mood] }} />
            <span style={{ color: MOOD_COLORS[todaysEntry.mood], fontWeight: 600 }}>
              {MOOD_LABELS[todaysEntry.mood] || ''}
            </span>
          </div>
          <p style={s.todayPreview}>
            {todaysEntry.text.length > 200
              ? todaysEntry.text.slice(0, 200) + '…'
              : todaysEntry.text}
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

      {/* Write form */}
      {writeMode && (
        <form onSubmit={handleSave} style={s.writeForm}>
          <div style={s.writeHeader}>
            <span style={s.writeDate}>{today}</span>
            <button type="button" onClick={() => setWriteMode(false)} style={s.closeBtn}>✕</button>
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
                  borderColor: form.mood === m ? MOOD_COLORS[m] : 'var(--border)',
                  backgroundColor: form.mood === m ? `${MOOD_COLORS[m]}22` : 'transparent',
                  color: form.mood === m ? MOOD_COLORS[m] : 'var(--muted)',
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
            {todaysEntry && (
              <button type="button" onClick={() => handleDelete(todaysEntry.id)} style={s.deleteBtn}>
                Delete entry
              </button>
            )}
            <button type="submit" disabled={saving || !form.text.trim()} style={s.primaryBtn}>
              {saving ? 'Saving...' : todaysEntry ? 'Update' : 'Save Entry'}
            </button>
          </div>
        </form>
      )}

      {/* Past entries */}
      {entries.length > 0 && (
        <>
          <div style={s.sectionHeader}>Past Entries</div>
          <div style={s.entryGrid}>
            {entries.map(entry => (
              <EntryCard
                key={entry.id}
                entry={entry}
                isToday={entry.date === today}
                selected={selected?.id === entry.id}
                onSelect={() => setSelected(selected?.id === entry.id ? null : entry)}
                onDelete={() => handleDelete(entry.id)}
              />
            ))}
          </div>
        </>
      )}

      {/* Read modal / expanded view */}
      {selected && !writeMode && (
        <div style={s.readPanel}>
          <div style={s.readHeader}>
            <span style={s.readDate}>{selected.date}</span>
            <div style={s.readMood}>
              <span style={{ ...s.moodDot, backgroundColor: MOOD_COLORS[selected.mood] }} />
              <span style={{ color: MOOD_COLORS[selected.mood] }}>{MOOD_LABELS[selected.mood]}</span>
            </div>
            <button onClick={() => setSelected(null)} style={s.closeBtn}>✕</button>
          </div>
          <p style={s.readBody}>{selected.text}</p>
        </div>
      )}
    </PageShell>
  )
}

function EntryCard({ entry, isToday, selected, onSelect, onDelete }) {
  const mood = entry.mood || 3
  const color = MOOD_COLORS[mood]

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
        <span style={{ ...s.moodDot, backgroundColor: color, width: 8, height: 8 }} />
        <span style={{ fontSize: '0.68rem', color, fontFamily: "'JetBrains Mono', monospace" }}>{MOOD_LABELS[mood]}</span>
      </div>
      <p style={s.entryPreview}>
        {entry.text.length > 120 ? entry.text.slice(0, 120) + '…' : entry.text}
      </p>
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
  todayBanner: {
    backgroundColor: 'var(--surface)', border: '1px solid var(--amber)', borderRadius: 10,
    padding: '16px 20px', marginBottom: 24,
  },
  todayLabel: { fontSize: '0.65rem', fontFamily: "'JetBrains Mono', monospace", color: 'var(--amber)', letterSpacing: '0.08em', marginBottom: 6 },
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
  closeBtn: { background: 'none', border: 'none', color: 'var(--muted)', cursor: 'pointer', fontSize: '0.9rem' },
  moodRow: { display: 'flex', alignItems: 'center', gap: 6, marginBottom: 14, flexWrap: 'wrap' },
  moodLabel: { fontSize: '0.72rem', color: 'var(--muted)', fontFamily: "'JetBrains Mono', monospace", marginRight: 4 },
  moodBtn: {
    border: '1px solid', borderRadius: 20, padding: '3px 12px',
    fontSize: '0.75rem', cursor: 'pointer', fontFamily: 'inherit',
    transition: 'all 0.15s', background: 'none',
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
    position: 'fixed', bottom: 24, right: 24, width: 420, maxWidth: 'calc(100vw - 48px)',
    backgroundColor: 'var(--surface)', border: '1px solid var(--amber)', borderRadius: 12,
    padding: '20px', boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
    maxHeight: '60vh', overflowY: 'auto', zIndex: 100,
  },
  readHeader: { display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 },
  readDate: { fontSize: '0.72rem', fontFamily: "'JetBrains Mono', monospace", color: 'var(--muted)', flex: 1 },
  readMood: { display: 'flex', alignItems: 'center', gap: 5, fontSize: '0.75rem' },
  readBody: { fontSize: '0.88rem', color: 'var(--text)', lineHeight: 1.7, whiteSpace: 'pre-wrap' },
  empty: { padding: '48px 0', color: 'var(--muted)', fontSize: '0.85rem', textAlign: 'center' },
}
