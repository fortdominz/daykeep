import { useState } from 'react'
import { api } from '../api'

const STATUS_OPTIONS = ['Planned', 'Complete', 'Incomplete', 'Skipped', 'Postponed']

const STATUS_COLOR = {
  'Complete':              'var(--green)',
  'Planned':               'var(--blue)',
  'Incomplete':            'var(--red)',
  'Skipped':               'var(--muted)',
  'Postponed':             'var(--amber)',
  'Abandoned: needs update': 'var(--red)',
}

export default function TaskItem({ task, onStatusChange, onRefresh }) {
  const [expanded, setExpanded] = useState(false)
  const [noteText, setNoteText] = useState('')
  const [addingNote, setAddingNote] = useState(false)

  const color = STATUS_COLOR[task.status] || 'var(--muted)'

  async function handleNote(e) {
    e.preventDefault()
    if (!noteText.trim()) return
    setAddingNote(true)
    try {
      await api.addNote(task.id, noteText.trim())
      setNoteText('')
      onRefresh()
    } catch (err) {
      alert(err.message)
    } finally {
      setAddingNote(false)
    }
  }

  async function handleDeleteNote(index) {
    if (!confirm('Delete this note?')) return
    try {
      await api.deleteNote(task.id, index)
      onRefresh()
    } catch (err) {
      alert(err.message)
    }
  }

  return (
    <div style={s.card}>
      {/* Main row */}
      <div style={s.row} onClick={() => setExpanded(x => !x)}>
        {/* Checkbox-style indicator */}
        <div style={{ ...s.dot, backgroundColor: task.status === 'Complete' ? 'var(--green)' : 'transparent', borderColor: color }} />

        <div style={s.titleWrap}>
          <span style={{ ...s.title, textDecoration: task.status === 'Complete' ? 'line-through' : 'none', color: task.status === 'Complete' ? 'var(--muted)' : '#e6edf3' }}>
            {task.title}
          </span>
          {task.scheduled_time && (
            <span style={s.time}>{task.scheduled_time}</span>
          )}
          {task.is_routine && (
            <span style={s.badge}>routine</span>
          )}
        </div>

        <select
          value={task.status}
          onChange={e => { e.stopPropagation(); onStatusChange(task.id, e.target.value) }}
          onClick={e => e.stopPropagation()}
          style={{ ...s.statusSelect, color }}
        >
          {STATUS_OPTIONS.map(opt => (
            <option key={opt} value={opt}>{opt}</option>
          ))}
        </select>

        <span style={{ ...s.chevron, transform: expanded ? 'rotate(90deg)' : 'none' }}>›</span>
      </div>

      {/* Expanded panel */}
      {expanded && (
        <div style={s.panel}>
          {/* Meta */}
          <div style={s.meta}>
            {task.category && <span style={s.chip}>{task.category}{task.subcategory ? ` › ${task.subcategory}` : ''}</span>}
            {task.date && <span style={s.chip}>📅 {task.date}</span>}
            {task.postpone_history?.length > 0 && <span style={s.chip}>↩ {task.postpone_history.length}x postponed</span>}
          </div>

          {/* Notes */}
          {task.notes?.length > 0 && (
            <div style={s.notes}>
              {task.notes.map((note, i) => (
                <div key={i} style={s.note}>
                  <span style={s.noteDot}>·</span>
                  <span style={s.noteText}>{note.text}</span>
                  <button onClick={() => handleDeleteNote(i)} style={s.noteDelete}>✕</button>
                </div>
              ))}
            </div>
          )}

          {/* Add note form */}
          <form onSubmit={handleNote} style={s.noteForm}>
            <input
              value={noteText}
              onChange={e => setNoteText(e.target.value)}
              placeholder="Add a note..."
              style={s.noteInput}
              disabled={addingNote}
            />
            <button type="submit" disabled={addingNote || !noteText.trim()} style={s.noteBtn}>
              Add
            </button>
          </form>
        </div>
      )}
    </div>
  )
}

const s = {
  card: {
    backgroundColor: 'var(--surface)',
    border: '1px solid var(--border)',
    borderRadius: 8,
    overflow: 'hidden',
    transition: 'border-color 0.15s',
  },
  row: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
    padding: '10px 14px',
    cursor: 'pointer',
  },
  dot: {
    width: 14,
    height: 14,
    borderRadius: '50%',
    border: '2px solid',
    flexShrink: 0,
    transition: 'background-color 0.15s',
  },
  titleWrap: {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    flexWrap: 'wrap',
    minWidth: 0,
  },
  title: {
    fontSize: '0.875rem',
    fontWeight: 500,
    transition: 'color 0.15s',
  },
  time: {
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: '0.7rem',
    color: 'var(--amber)',
  },
  badge: {
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: '0.65rem',
    color: 'var(--muted)',
    backgroundColor: 'var(--surface-2)',
    border: '1px solid var(--border)',
    borderRadius: 10,
    padding: '1px 6px',
  },
  statusSelect: {
    backgroundColor: 'transparent',
    border: 'none',
    outline: 'none',
    fontSize: '0.75rem',
    fontFamily: "'JetBrains Mono', monospace",
    fontWeight: 600,
    cursor: 'pointer',
    padding: '2px 4px',
    width: 'auto',
    flexShrink: 0,
  },
  chevron: {
    color: 'var(--muted)',
    fontSize: '1rem',
    transition: 'transform 0.15s',
    flexShrink: 0,
  },
  panel: {
    borderTop: '1px solid var(--border)',
    padding: '10px 14px 12px',
    backgroundColor: 'var(--bg)',
  },
  meta: {
    display: 'flex',
    gap: 6,
    flexWrap: 'wrap',
    marginBottom: 10,
  },
  chip: {
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: '0.68rem',
    color: 'var(--muted)',
    backgroundColor: 'var(--surface-2)',
    border: '1px solid var(--border)',
    borderRadius: 4,
    padding: '2px 7px',
  },
  notes: {
    display: 'flex',
    flexDirection: 'column',
    gap: 4,
    marginBottom: 10,
  },
  note: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: 6,
    fontSize: '0.82rem',
    color: 'var(--muted)',
  },
  noteDot: {
    color: 'var(--amber)',
    flexShrink: 0,
    lineHeight: 1.6,
  },
  noteText: {
    flex: 1,
  },
  noteDelete: {
    background: 'none',
    border: 'none',
    color: 'var(--muted)',
    cursor: 'pointer',
    fontSize: '0.7rem',
    padding: 2,
    flexShrink: 0,
  },
  noteForm: {
    display: 'flex',
    gap: 8,
  },
  noteInput: {
    flex: 1,
    fontSize: '0.8rem',
    padding: '6px 10px',
    width: 'auto',
  },
  noteBtn: {
    backgroundColor: 'var(--surface-2)',
    border: '1px solid var(--border)',
    color: 'var(--muted)',
    borderRadius: 6,
    padding: '6px 14px',
    fontSize: '0.78rem',
    cursor: 'pointer',
    whiteSpace: 'nowrap',
  },
}
