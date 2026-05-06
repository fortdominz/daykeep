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
  return MOOD_COLORS[Number(mood)] || 'var(--muted)'
}
function getMoodLabel(mood) {
  return MOOD_LABELS[Number(mood)] || ''
}
function getEntryText(entry) {
  return entry?.content || entry?.text || entry?.entry || ''
}
function formatTime(dateCreated) {
  if (!dateCreated) return ''
  try {
    const d = new Date(dateCreated.replace(' ', 'T'))
    return d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })
  } catch { return '' }
}

// ─── WRITE FORM ──────────────────────────────────────────────────────────────

function WriteForm({ entry, onSave, onCancel, onDelete }) {
  const [text, setText] = useState(entry ? getEntryText(entry) : '')
  const [mood, setMood] = useState(entry ? Number(entry.mood) || 3 : 3)
  const [saving, setSaving] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    if (!text.trim()) return
    setSaving(true)
    try {
      await onSave(text.trim(), mood)
    } finally {
      setSaving(false)
    }
  }

  const isEdit = !!entry

  return (
    <form onSubmit={handleSubmit} style={s.writeForm}>
      <div style={s.formTop}>
        <span style={s.formLabel}>{isEdit ? 'Edit entry' : 'New entry'}</span>
        <button type="button" onClick={onCancel} style={s.closeBtn}>✕ Close</button>
      </div>

      {/* Mood picker */}
      <div style={s.moodRow}>
        <span style={s.moodLabel}>Mood</span>
        {[1, 2, 3, 4, 5].map(m => (
          <button
            key={m}
            type="button"
            onClick={() => setMood(m)}
            style={{
              ...s.moodBtn,
              borderColor: mood === m ? getMoodColor(m) : 'var(--border)',
              backgroundColor: mood === m ? `${getMoodColor(m)}22` : 'transparent',
              color: mood === m ? getMoodColor(m) : 'var(--muted)',
            }}
          >
            {MOOD_LABELS[m]}
          </button>
        ))}
      </div>

      <textarea
        value={text}
        onChange={e => setText(e.target.value)}
        placeholder="What's on your mind?"
        rows={6}
        style={s.textarea}
        autoFocus
      />

      <div style={s.formActions}>
        {isEdit && onDelete && (
          <button type="button" onClick={onDelete} style={s.deleteBtn}>
            Delete
          </button>
        )}
        <button
          type="submit"
          disabled={saving || !text.trim()}
          style={{ ...s.primaryBtn, opacity: (!text.trim() && !saving) ? 0.5 : 1 }}
        >
          {saving ? 'Saving...' : isEdit ? 'Save changes' : 'Save entry'}
        </button>
      </div>
    </form>
  )
}

// ─── PAST ENTRY MODAL ────────────────────────────────────────────────────────

function PastEntryModal({ entry, onClose }) {
  if (!entry) return null
  const text = getEntryText(entry)
  const mood = Number(entry.mood)

  return (
    <div style={s.modalOverlay} onClick={onClose}>
      <div style={s.modalBox} onClick={e => e.stopPropagation()}>
        <div style={s.modalHeader}>
          <div style={s.modalDate}>{entry.date}</div>
          {mood > 0 && (
            <div style={s.modalMood}>
              <span style={{ ...s.moodDot, backgroundColor: getMoodColor(mood) }} />
              <span style={{ color: getMoodColor(mood), fontWeight: 600 }}>{getMoodLabel(mood)}</span>
            </div>
          )}
          <button onClick={onClose} style={s.closeBtn}>✕ Close</button>
        </div>
        <div style={s.modalTime}>{formatTime(entry.date_created)}</div>
        <p style={s.modalBody}>{text}</p>
      </div>
    </div>
  )
}

// ─── MAIN COMPONENT ──────────────────────────────────────────────────────────

export default function Journal() {
  const today = new Date().toISOString().split('T')[0]

  const [allEntries, setAllEntries] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Form state: null = closed, 'new' = new entry, entry object = editing
  const [formMode, setFormMode] = useState(null)

  // Past entry modal
  const [modalEntry, setModalEntry] = useState(null)

  const load = useCallback(async () => {
    setError(null)
    try {
      const all = await api.getJournal()
      setAllEntries(Array.isArray(all) ? all : [])
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const todaysEntries = allEntries.filter(e => e.date === today)
    .sort((a, b) => (b.date_created || '').localeCompare(a.date_created || ''))

  const pastEntries = allEntries.filter(e => e.date < today)
    .sort((a, b) => b.date.localeCompare(a.date))

  // ── handlers ──

  async function handleNew(text, mood) {
    await api.createJournal({ text, mood })
    setFormMode(null)
    load()
  }

  async function handleEdit(entry, text, mood) {
    await api.updateJournal(entry.id, { text, mood })
    setFormMode(null)
    load()
  }

  async function handleDelete(id) {
    if (!confirm('Delete this entry?')) return
    await api.deleteJournal(id)
    setFormMode(null)
    load()
  }

  function openEdit(entry) {
    setFormMode(entry)  // entry object = editing that entry
  }

  function openNew() {
    setFormMode('new')
  }

  function closeForm() {
    setFormMode(false)
  }

  // ── render ──

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

  const isEditing = formMode && formMode !== 'new'
  const isNew = formMode === 'new'

  return (
    <PageShell>
      {/* Header */}
      <div style={s.header}>
        <div>
          <h1 style={s.pageTitle}>Journal</h1>
          <p style={s.subtitle}>{allEntries.length} entr{allEntries.length !== 1 ? 'ies' : 'y'}</p>
        </div>
        {!formMode && (
          <button onClick={openNew} style={s.primaryBtn}>+ New Entry</button>
        )}
      </div>

      {/* New entry form */}
      {isNew && (
        <WriteForm
          entry={null}
          onSave={handleNew}
          onCancel={closeForm}
        />
      )}

      {/* ── Today's entries ── */}
      <div style={s.sectionHeader}>
        <span style={s.sectionTitle}>Today — {today}</span>
        <span style={s.sectionCount}>{todaysEntries.length}</span>
      </div>

      {todaysEntries.length === 0 ? (
        <div style={s.emptyToday}>
          Nothing written yet today.{' '}
          <button onClick={openNew} style={s.inlineLink}>Write something →</button>
        </div>
      ) : (
        <div style={s.todayList}>
          {todaysEntries.map(entry => {
            const isEditingThis = isEditing && formMode?.id === entry.id
            return (
              <div key={entry.id} style={s.todayCard}>
                {isEditingThis ? (
                  <WriteForm
                    entry={entry}
                    onSave={(text, mood) => handleEdit(entry, text, mood)}
                    onCancel={closeForm}
                    onDelete={() => handleDelete(entry.id)}
                  />
                ) : (
                  <>
                    <div style={s.todayCardTop}>
                      {Number(entry.mood) > 0 && (
                        <div style={s.moodPill}>
                          <span style={{ ...s.moodDot, backgroundColor: getMoodColor(entry.mood) }} />
                          <span style={{ color: getMoodColor(entry.mood), fontWeight: 600 }}>
                            {getMoodLabel(entry.mood)}
                          </span>
                        </div>
                      )}
                      <span style={s.entryTime}>{formatTime(entry.date_created)}</span>
                      <button
                        onClick={() => openEdit(entry)}
                        style={s.editBtn}
                        disabled={!!formMode}
                      >
                        ✎ Edit
                      </button>
                    </div>
                    <p style={s.todayText}>{getEntryText(entry)}</p>
                  </>
                )}
              </div>
            )
          })}
        </div>
      )}

      {/* ── Past entries ── */}
      {pastEntries.length > 0 && (
        <>
          <div style={{ ...s.sectionHeader, marginTop: 32 }}>
            <span style={s.sectionTitle}>Past Entries</span>
            <span style={s.sectionCount}>{pastEntries.length}</span>
          </div>
          <div style={s.pastGrid}>
            {pastEntries.map(entry => {
              const mood = Number(entry.mood)
              const text = getEntryText(entry)
              return (
                <div
                  key={entry.id}
                  onClick={() => setModalEntry(entry)}
                  style={s.pastCard}
                  title="Click to read"
                >
                  <div style={s.pastCardTop}>
                    <span style={s.pastDate}>{entry.date}</span>
                    {mood > 0 && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                        <span style={{ ...s.moodDot, width: 7, height: 7, backgroundColor: getMoodColor(mood) }} />
                        <span style={{ fontSize: '0.68rem', color: getMoodColor(mood), fontFamily: "'JetBrains Mono', monospace" }}>
                          {getMoodLabel(mood)}
                        </span>
                      </div>
                    )}
                  </div>
                  <p style={s.pastPreview}>
                    {text.length > 110 ? text.slice(0, 110) + '…' : text || '(no content)'}
                  </p>
                  <span style={s.expandHint}>↗ Read</span>
                </div>
              )
            })}
          </div>
        </>
      )}

      {/* Past entry full-screen modal */}
      {modalEntry && (
        <PastEntryModal entry={modalEntry} onClose={() => setModalEntry(null)} />
      )}
    </PageShell>
  )
}

// ─── SHARED ──────────────────────────────────────────────────────────────────

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

// ─── STYLES ──────────────────────────────────────────────────────────────────

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

  // Write form
  writeForm: {
    backgroundColor: 'var(--surface)', border: '1px solid var(--amber)',
    borderRadius: 10, padding: '18px 20px', marginBottom: 20,
  },
  formTop: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 },
  formLabel: { fontSize: '0.72rem', fontFamily: "'JetBrains Mono', monospace", color: 'var(--amber)', textTransform: 'uppercase', letterSpacing: '0.06em' },
  closeBtn: { background: 'none', border: 'none', color: 'var(--muted)', cursor: 'pointer', fontSize: '0.75rem', fontFamily: "'JetBrains Mono', monospace" },
  moodRow: { display: 'flex', alignItems: 'center', gap: 6, marginBottom: 12, flexWrap: 'wrap' },
  moodLabel: { fontSize: '0.7rem', color: 'var(--muted)', fontFamily: "'JetBrains Mono', monospace", marginRight: 4 },
  moodBtn: {
    border: '1px solid', borderRadius: 20, padding: '3px 11px', fontSize: '0.73rem',
    cursor: 'pointer', fontFamily: 'inherit', transition: 'all 0.15s', background: 'none',
  },
  textarea: {
    width: '100%', backgroundColor: 'var(--bg)', border: '1px solid var(--border)',
    borderRadius: 8, padding: '12px 14px', color: 'var(--text)', fontFamily: 'inherit',
    fontSize: '0.9rem', lineHeight: 1.7, resize: 'vertical', outline: 'none',
    transition: 'border-color 0.15s', minHeight: 120,
  },
  formActions: { marginTop: 12, display: 'flex', justifyContent: 'flex-end', gap: 10, alignItems: 'center' },
  deleteBtn: { background: 'none', border: 'none', color: 'var(--red)', cursor: 'pointer', fontSize: '0.78rem', fontFamily: 'inherit', marginRight: 'auto' },

  // Section headers
  sectionHeader: {
    display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12,
    paddingBottom: 8, borderBottom: '1px solid var(--border)',
  },
  sectionTitle: { fontSize: '0.72rem', fontFamily: "'JetBrains Mono', monospace", color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.06em' },
  sectionCount: {
    fontSize: '0.7rem', fontFamily: "'JetBrains Mono', monospace", color: 'var(--muted)',
    backgroundColor: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 10, padding: '1px 7px',
  },

  // Today's entries
  emptyToday: { fontSize: '0.85rem', color: 'var(--muted)', padding: '20px 0', marginBottom: 8 },
  inlineLink: { background: 'none', border: 'none', color: 'var(--amber)', cursor: 'pointer', fontFamily: 'inherit', fontSize: '0.85rem', fontWeight: 600 },
  todayList: { display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 8 },
  todayCard: {
    backgroundColor: 'var(--surface)', border: '1px solid var(--border)',
    borderRadius: 10, overflow: 'hidden',
  },
  todayCardTop: { display: 'flex', alignItems: 'center', gap: 10, padding: '12px 16px 0' },
  moodPill: { display: 'flex', alignItems: 'center', gap: 5, fontSize: '0.78rem' },
  moodDot: { width: 9, height: 9, borderRadius: '50%', display: 'inline-block', flexShrink: 0 },
  entryTime: { fontSize: '0.68rem', fontFamily: "'JetBrains Mono', monospace", color: 'var(--muted)', flex: 1 },
  editBtn: {
    background: 'none', border: '1px solid var(--border)', color: 'var(--muted)',
    borderRadius: 5, padding: '3px 10px', fontSize: '0.72rem', cursor: 'pointer',
    fontFamily: "'JetBrains Mono', monospace", transition: 'color 0.15s, border-color 0.15s',
  },
  todayText: { padding: '10px 16px 14px', fontSize: '0.9rem', color: 'var(--text)', lineHeight: 1.65, whiteSpace: 'pre-wrap' },

  // Past entries
  pastGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 10 },
  pastCard: {
    backgroundColor: 'var(--surface)', border: '1px solid var(--border)',
    borderRadius: 8, padding: '12px 14px', cursor: 'pointer',
    transition: 'border-color 0.15s',
    position: 'relative',
  },
  pastCardTop: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 },
  pastDate: { fontSize: '0.72rem', fontFamily: "'JetBrains Mono', monospace", color: 'var(--muted)' },
  pastPreview: { fontSize: '0.8rem', color: 'var(--muted)', lineHeight: 1.5, marginBottom: 8 },
  expandHint: { fontSize: '0.65rem', fontFamily: "'JetBrains Mono', monospace", color: 'var(--border)' },

  // Modal
  modalOverlay: {
    position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.7)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    zIndex: 200, padding: 24,
  },
  modalBox: {
    backgroundColor: 'var(--surface)', border: '1px solid var(--amber)',
    borderRadius: 14, padding: '28px 32px', maxWidth: 640, width: '100%',
    maxHeight: '80vh', overflowY: 'auto',
    boxShadow: '0 16px 48px rgba(0,0,0,0.6)',
  },
  modalHeader: { display: 'flex', alignItems: 'center', gap: 12, marginBottom: 4 },
  modalDate: { fontSize: '0.8rem', fontFamily: "'JetBrains Mono', monospace", color: 'var(--amber)', flex: 1 },
  modalMood: { display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.85rem' },
  modalTime: { fontSize: '0.65rem', fontFamily: "'JetBrains Mono', monospace", color: 'var(--muted)', marginBottom: 20 },
  modalBody: { fontSize: '1rem', color: 'var(--text)', lineHeight: 1.8, whiteSpace: 'pre-wrap' },

  // Error / misc
  errorBox: { padding: '32px', backgroundColor: 'var(--surface)', border: '1px solid var(--red)', borderRadius: 10 },
  errorTitle: { fontWeight: 700, color: 'var(--red)', marginBottom: 6, fontSize: '0.9rem' },
  errorMsg: { color: 'var(--muted)', fontFamily: "'JetBrains Mono', monospace", fontSize: '0.78rem', marginBottom: 16 },
  retryBtn: { background: 'none', border: '1px solid var(--red)', color: 'var(--red)', borderRadius: 6, padding: '6px 16px', cursor: 'pointer', fontFamily: 'inherit', fontSize: '0.78rem' },
}
