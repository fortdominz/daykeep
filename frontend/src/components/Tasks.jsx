import { useState, useEffect, useCallback } from 'react'
import { api } from '../api'
import TaskItem from './TaskItem'

export default function Tasks() {
  const [tasks, setTasks] = useState([])
  const [goals, setGoals] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('today')  // today | all | planned | complete
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ title: '', date: '', scheduled_time: '', category: '', goal_id: '', is_routine: false })
  const [saving, setSaving] = useState(false)

  const load = useCallback(async () => {
    try {
      const [t, g] = await Promise.all([api.getTasks(), api.getGoals()])
      setTasks(t)
      setGoals(g)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const today = new Date().toISOString().split('T')[0]

  const filtered = tasks.filter(t => {
    if (filter === 'today')    return t.date === today
    if (filter === 'planned')  return t.status === 'Planned'
    if (filter === 'complete') return t.status === 'Complete'
    if (filter === 'abandoned') return t.status === 'Abandoned: needs update'
    return true
  }).sort((a, b) => b.date.localeCompare(a.date))

  async function handleCreate(e) {
    e.preventDefault()
    if (!form.title.trim()) return
    setSaving(true)
    try {
      await api.createTask({
        title: form.title.trim(),
        date: form.date || today,
        scheduled_time: form.scheduled_time,
        category: form.category,
        goal_id: form.goal_id ? parseInt(form.goal_id) : null,
        is_routine: form.is_routine,
      })
      setForm({ title: '', date: '', scheduled_time: '', category: '', goal_id: '', is_routine: false })
      setShowForm(false)
      load()
    } catch (e) {
      alert(e.message)
    } finally {
      setSaving(false)
    }
  }

  async function handleStatusChange(taskId, status) {
    await api.updateTask(taskId, { status })
    load()
  }

  if (loading) return <PageShell><Loading /></PageShell>

  return (
    <PageShell>
      <div style={s.header}>
        <h1 style={s.pageTitle}>Tasks</h1>
        <button onClick={() => setShowForm(x => !x)} style={s.primaryBtn}>
          {showForm ? '✕ Cancel' : '+ New Task'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} style={s.form}>
          <div style={s.formGrid}>
            <div style={s.field}>
              <label style={s.label}>Title *</label>
              <input value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} placeholder="What do you need to do?" required />
            </div>
            <div style={s.field}>
              <label style={s.label}>Date</label>
              <input type="date" value={form.date} onChange={e => setForm(f => ({ ...f, date: e.target.value }))} />
            </div>
            <div style={s.field}>
              <label style={s.label}>Time</label>
              <input type="time" value={form.scheduled_time} onChange={e => setForm(f => ({ ...f, scheduled_time: e.target.value }))} />
            </div>
            <div style={s.field}>
              <label style={s.label}>Category</label>
              <input value={form.category} onChange={e => setForm(f => ({ ...f, category: e.target.value }))} placeholder="e.g. Health, School..." />
            </div>
            <div style={s.field}>
              <label style={s.label}>Link to Goal</label>
              <select value={form.goal_id} onChange={e => setForm(f => ({ ...f, goal_id: e.target.value }))}>
                <option value="">No goal</option>
                {goals.map(g => <option key={g.id} value={g.id}>{g.title}</option>)}
              </select>
            </div>
            <div style={{ ...s.field, justifyContent: 'flex-end', flexDirection: 'row', alignItems: 'center', gap: 8 }}>
              <label style={s.label}>Routine</label>
              <input type="checkbox" checked={form.is_routine} onChange={e => setForm(f => ({ ...f, is_routine: e.target.checked }))} style={{ width: 'auto' }} />
            </div>
          </div>
          <div style={s.formActions}>
            <button type="submit" disabled={saving} style={s.primaryBtn}>
              {saving ? 'Saving...' : 'Create Task'}
            </button>
          </div>
        </form>
      )}

      {/* Filters */}
      <div style={s.filters}>
        {['today', 'all', 'planned', 'complete', 'abandoned'].map(f => (
          <button key={f} onClick={() => setFilter(f)} style={{ ...s.filterBtn, ...(filter === f ? s.filterActive : {}) }}>
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
        <span style={s.filterCount}>{filtered.length} tasks</span>
      </div>

      {/* List */}
      {filtered.length === 0 ? (
        <div style={s.empty}>No tasks in this view.</div>
      ) : (
        <div style={s.list}>
          {filtered.map(task => (
            <TaskItem key={task.id} task={task} onStatusChange={handleStatusChange} onRefresh={load} />
          ))}
        </div>
      )}
    </PageShell>
  )
}

function Loading() {
  return <div style={{ padding: 48, textAlign: 'center', color: 'var(--muted)' }}>Loading...</div>
}

function PageShell({ children }) {
  return <div style={s.page}>{children}</div>
}

const s = {
  page: { padding: '32px 36px', maxWidth: 860, animation: 'fadeIn 0.2s ease' },
  header: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 },
  pageTitle: { fontSize: '1.8rem', fontWeight: 700, color: '#e6edf3', lineHeight: 1.1 },
  primaryBtn: {
    backgroundColor: 'var(--amber)', color: '#0d1117', border: 'none',
    borderRadius: 6, padding: '8px 18px', fontWeight: 700, fontSize: '0.82rem',
    cursor: 'pointer', fontFamily: 'inherit',
  },
  form: {
    backgroundColor: 'var(--surface)', border: '1px solid var(--border)',
    borderRadius: 10, padding: '20px', marginBottom: 24,
  },
  formGrid: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 },
  field: { display: 'flex', flexDirection: 'column', gap: 4 },
  label: { fontSize: '0.72rem', fontFamily: "'JetBrains Mono', monospace", color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.04em' },
  formActions: { marginTop: 16, display: 'flex', justifyContent: 'flex-end' },
  filters: { display: 'flex', gap: 6, marginBottom: 16, alignItems: 'center', flexWrap: 'wrap' },
  filterBtn: {
    backgroundColor: 'var(--surface)', border: '1px solid var(--border)',
    color: 'var(--muted)', borderRadius: 20, padding: '4px 14px',
    fontSize: '0.78rem', cursor: 'pointer', fontFamily: 'inherit', transition: 'all 0.15s',
  },
  filterActive: { backgroundColor: 'var(--amber-dim)', borderColor: 'var(--amber)', color: 'var(--amber-bright)' },
  filterCount: { marginLeft: 'auto', fontSize: '0.7rem', color: 'var(--muted)', fontFamily: "'JetBrains Mono', monospace" },
  list: { display: 'flex', flexDirection: 'column', gap: 6 },
  empty: { padding: '40px 0', color: 'var(--muted)', fontSize: '0.85rem', textAlign: 'center', fontFamily: "'JetBrains Mono', monospace" },
}
