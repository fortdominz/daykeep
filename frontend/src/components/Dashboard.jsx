import { useState, useEffect, useCallback } from 'react'
import { api } from '../api'
import TaskItem from './TaskItem'

const MOOD_LABELS = { 1: 'Rough', 2: 'Low', 3: 'Okay', 4: 'Good', 5: 'Great' }

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [newTask, setNewTask] = useState('')
  const [adding, setAdding] = useState(false)

  const load = useCallback(async () => {
    try {
      const d = await api.dashboard()
      setData(d)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  async function handleAddTask(e) {
    e.preventDefault()
    if (!newTask.trim()) return
    setAdding(true)
    try {
      await api.createTask({ title: newTask.trim() })
      setNewTask('')
      load()
    } catch (e) {
      alert(e.message)
    } finally {
      setAdding(false)
    }
  }

  async function handleStatusChange(taskId, status) {
    await api.updateTask(taskId, { status })
    load()
  }

  if (loading) return <PageShell><LoadingDots /></PageShell>
  if (error) return <PageShell><ErrorMsg msg={error} /></PageShell>

  const { summary, tasks_today, upcoming, overdue, endangered_streaks, abandoned_count } = data
  const completionPct = summary.completion_rate

  const today = new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })

  return (
    <PageShell>
      {/* Header */}
      <div style={s.header}>
        <div>
          <h1 style={s.pageTitle}>Today</h1>
          <p style={s.dateLabel}>{today}</p>
        </div>
        {abandoned_count > 0 && (
          <div style={s.abandonedBadge}>
            ⚠ {abandoned_count} task{abandoned_count !== 1 ? 's' : ''} need{abandoned_count === 1 ? 's' : ''} attention
          </div>
        )}
      </div>

      {/* Stats row */}
      <div style={s.statsRow}>
        <StatCard label="Completion" value={`${completionPct}%`} accent />
        <StatCard label="Complete" value={summary.completed} color="var(--green)" />
        <StatCard label="Planned" value={summary.planned} color="var(--blue)" />
        <StatCard label="Incomplete" value={summary.incomplete} color="var(--red)" />
        <StatCard label="Total" value={summary.total} />
      </div>

      {/* Progress bar */}
      {summary.total > 0 && (
        <div style={s.progressWrap}>
          <div style={s.progressTrack}>
            <div style={{ ...s.progressFill, width: `${completionPct}%` }} />
          </div>
          <span style={s.progressLabel}>{completionPct}% done</span>
        </div>
      )}

      {/* Alerts */}
      {endangered_streaks.length > 0 && (
        <div style={s.alert}>
          <span style={s.alertIcon}>🔥</span>
          <span>
            <strong>Streak at risk:</strong>{' '}
            {endangered_streaks.map(g => g.title).join(', ')} — complete today's task to keep the streak.
          </span>
        </div>
      )}
      {overdue.length > 0 && (
        <div style={{ ...s.alert, borderColor: 'var(--red)', backgroundColor: 'var(--red-dim)' }}>
          <span style={s.alertIcon}>⏰</span>
          <span><strong>{overdue.length} task{overdue.length !== 1 ? 's' : ''} overdue</strong> — scheduled time has passed.</span>
        </div>
      )}
      {upcoming.length > 0 && (
        <div style={{ ...s.alert, borderColor: 'var(--amber)', backgroundColor: 'var(--amber-dim)' }}>
          <span style={s.alertIcon}>⏱</span>
          <span>
            <strong>Coming up:</strong>{' '}
            {upcoming.map(u => `${u.task.title} in ${u.minutes_until}m`).join('  ·  ')}
          </span>
        </div>
      )}

      {/* Quick add */}
      <form onSubmit={handleAddTask} style={s.quickAdd}>
        <input
          value={newTask}
          onChange={e => setNewTask(e.target.value)}
          placeholder="Add a task for today..."
          style={s.quickInput}
          disabled={adding}
        />
        <button type="submit" disabled={adding || !newTask.trim()} style={s.addBtn}>
          {adding ? '...' : '+ Add'}
        </button>
      </form>

      {/* Today's tasks */}
      <SectionHeader title={`Today's Tasks`} count={tasks_today.length} />
      {tasks_today.length === 0 ? (
        <EmptyState msg="No tasks yet. Add one above." />
      ) : (
        <div style={s.taskList}>
          {tasks_today.map(task => (
            <TaskItem key={task.id} task={task} onStatusChange={handleStatusChange} onRefresh={load} />
          ))}
        </div>
      )}
    </PageShell>
  )
}

function StatCard({ label, value, accent, color }) {
  return (
    <div style={{ ...s.statCard, ...(accent ? s.statCardAccent : {}) }}>
      <div style={{ ...s.statValue, color: accent ? 'var(--amber)' : color || 'var(--text)' }}>{value}</div>
      <div style={s.statLabel}>{label}</div>
    </div>
  )
}

function SectionHeader({ title, count }) {
  return (
    <div style={s.sectionHeader}>
      <span style={s.sectionTitle}>{title}</span>
      {count !== undefined && <span style={s.sectionCount}>{count}</span>}
    </div>
  )
}

function EmptyState({ msg }) {
  return <div style={s.empty}>{msg}</div>
}

function LoadingDots() {
  return (
    <div style={{ display: 'flex', gap: 6, padding: 48, justifyContent: 'center' }}>
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

function ErrorMsg({ msg }) {
  return <div style={{ padding: 32, color: 'var(--red)', fontFamily: 'JetBrains Mono, monospace', fontSize: '0.8rem' }}>Error: {msg}</div>
}

function PageShell({ children }) {
  return <div style={s.page}>{children}</div>
}

const s = {
  page: {
    padding: '32px 36px',
    maxWidth: 860,
    animation: 'fadeIn 0.2s ease',
  },
  header: {
    display: 'flex',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
    marginBottom: 24,
    flexWrap: 'wrap',
    gap: 12,
  },
  pageTitle: {
    fontSize: '1.8rem',
    fontWeight: 700,
    color: '#e6edf3',
    lineHeight: 1.1,
  },
  dateLabel: {
    fontSize: '0.8rem',
    color: 'var(--muted)',
    fontFamily: "'JetBrains Mono', monospace",
    marginTop: 4,
  },
  abandonedBadge: {
    backgroundColor: 'var(--red-dim)',
    border: '1px solid var(--red)',
    color: 'var(--red)',
    padding: '6px 14px',
    borderRadius: 6,
    fontSize: '0.78rem',
    fontWeight: 600,
  },
  statsRow: {
    display: 'flex',
    gap: 12,
    marginBottom: 16,
    flexWrap: 'wrap',
  },
  statCard: {
    flex: 1,
    minWidth: 80,
    backgroundColor: 'var(--surface)',
    border: '1px solid var(--border)',
    borderRadius: 8,
    padding: '12px 14px',
    textAlign: 'center',
  },
  statCardAccent: {
    borderColor: 'var(--amber)',
    backgroundColor: 'var(--amber-dim)',
  },
  statValue: {
    fontSize: '1.5rem',
    fontWeight: 700,
    lineHeight: 1,
    fontFamily: "'JetBrains Mono', monospace",
  },
  statLabel: {
    fontSize: '0.68rem',
    color: 'var(--muted)',
    marginTop: 4,
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
  },
  progressWrap: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
    marginBottom: 20,
  },
  progressTrack: {
    flex: 1,
    height: 4,
    backgroundColor: 'var(--surface-2)',
    borderRadius: 2,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: 'var(--amber)',
    borderRadius: 2,
    transition: 'width 0.4s ease',
  },
  progressLabel: {
    fontSize: '0.7rem',
    fontFamily: "'JetBrains Mono', monospace",
    color: 'var(--muted)',
    whiteSpace: 'nowrap',
  },
  alert: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: 10,
    backgroundColor: 'var(--green-dim)',
    border: '1px solid var(--green)',
    borderRadius: 8,
    padding: '10px 14px',
    fontSize: '0.82rem',
    marginBottom: 12,
    color: 'var(--text)',
  },
  alertIcon: {
    flexShrink: 0,
    marginTop: 1,
  },
  quickAdd: {
    display: 'flex',
    gap: 10,
    marginBottom: 24,
    marginTop: 8,
  },
  quickInput: {
    flex: 1,
    backgroundColor: 'var(--surface)',
    border: '1px solid var(--border)',
    borderRadius: 6,
    padding: '9px 14px',
    color: 'var(--text)',
    fontSize: '0.875rem',
    outline: 'none',
    transition: 'border-color 0.15s',
    width: 'auto',
  },
  addBtn: {
    backgroundColor: 'var(--amber)',
    color: '#0d1117',
    border: 'none',
    borderRadius: 6,
    padding: '9px 18px',
    fontWeight: 700,
    fontSize: '0.82rem',
    cursor: 'pointer',
    whiteSpace: 'nowrap',
    transition: 'background-color 0.15s',
  },
  sectionHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    marginBottom: 10,
    paddingBottom: 8,
    borderBottom: '1px solid var(--border)',
  },
  sectionTitle: {
    fontSize: '0.78rem',
    fontFamily: "'JetBrains Mono', monospace",
    color: 'var(--muted)',
    textTransform: 'uppercase',
    letterSpacing: '0.06em',
  },
  sectionCount: {
    backgroundColor: 'var(--surface-2)',
    border: '1px solid var(--border)',
    color: 'var(--muted)',
    borderRadius: 10,
    padding: '1px 7px',
    fontSize: '0.72rem',
    fontFamily: "'JetBrains Mono', monospace",
  },
  taskList: {
    display: 'flex',
    flexDirection: 'column',
    gap: 6,
  },
  empty: {
    padding: '32px 0',
    color: 'var(--muted)',
    fontSize: '0.85rem',
    textAlign: 'center',
    fontFamily: "'JetBrains Mono', monospace",
  },
}
