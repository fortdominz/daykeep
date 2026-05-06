import { useState, useEffect, useCallback } from 'react'
import { api } from '../api'

const STATUS_COLOR = {
  Active:   'var(--blue)',
  Achieved: 'var(--green)',
  Dropped:  'var(--muted)',
  Paused:   'var(--amber)',
}

export default function Goals() {
  const [goals, setGoals] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editGoal, setEditGoal] = useState(null)
  const [filter, setFilter] = useState('Active')
  const [form, setForm] = useState({ title: '', description: '', category: '', target_date: '', is_routine: false, routine_time: '', status: 'Active' })
  const [saving, setSaving] = useState(false)

  const load = useCallback(async () => {
    try {
      setGoals(await api.getGoals())
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  function openEdit(goal) {
    setEditGoal(goal)
    setForm({
      title: goal.title,
      description: goal.description || '',
      category: goal.category || '',
      target_date: goal.target_date || '',
      is_routine: goal.is_routine || false,
      routine_time: goal.routine_time || '',
      status: goal.status,
    })
    setShowForm(true)
  }

  function openCreate() {
    setEditGoal(null)
    setForm({ title: '', description: '', category: '', target_date: '', is_routine: false, routine_time: '', status: 'Active' })
    setShowForm(true)
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setSaving(true)
    try {
      if (editGoal) {
        await api.updateGoal(editGoal.id, form)
      } else {
        await api.createGoal(form)
      }
      setShowForm(false)
      setEditGoal(null)
      load()
    } catch (e) {
      alert(e.message)
    } finally {
      setSaving(false)
    }
  }

  async function handleDelete(id) {
    if (!confirm('Delete this goal? Associated tasks will remain.')) return
    await api.deleteGoal(id)
    load()
  }

  async function quickStatus(id, status) {
    await api.updateGoal(id, { status })
    load()
  }

  const filtered = goals.filter(g => filter === 'all' || g.status === filter)
  const activeCount = goals.filter(g => g.status === 'Active').length
  const achievedCount = goals.filter(g => g.status === 'Achieved').length

  if (loading) return <PageShell><div style={s.empty}>Loading...</div></PageShell>

  return (
    <PageShell>
      <div style={s.header}>
        <div>
          <h1 style={s.pageTitle}>Goals</h1>
          <p style={s.subtitle}>{activeCount} active · {achievedCount} achieved</p>
        </div>
        <button onClick={openCreate} style={s.primaryBtn}>+ New Goal</button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} style={s.form}>
          <div style={s.formTitle}>{editGoal ? 'Edit Goal' : 'New Goal'}</div>
          <div style={s.formGrid}>
            <div style={{ ...s.field, gridColumn: '1 / -1' }}>
              <label style={s.label}>Title *</label>
              <input value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} placeholder="What do you want to achieve?" required />
            </div>
            <div style={{ ...s.field, gridColumn: '1 / -1' }}>
              <label style={s.label}>Description</label>
              <textarea value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} placeholder="Why does this matter?" rows={2} />
            </div>
            <div style={s.field}>
              <label style={s.label}>Category</label>
              <input value={form.category} onChange={e => setForm(f => ({ ...f, category: e.target.value }))} placeholder="e.g. Health, Career..." />
            </div>
            <div style={s.field}>
              <label style={s.label}>Target Date</label>
              <input type="date" value={form.target_date} onChange={e => setForm(f => ({ ...f, target_date: e.target.value }))} />
            </div>
            <div style={s.field}>
              <label style={s.label}>Status</label>
              <select value={form.status} onChange={e => setForm(f => ({ ...f, status: e.target.value }))}>
                {['Active', 'Achieved', 'Paused', 'Dropped'].map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div style={{ ...s.field, flexDirection: 'row', alignItems: 'center', gap: 10 }}>
              <input type="checkbox" checked={form.is_routine} onChange={e => setForm(f => ({ ...f, is_routine: e.target.checked }))} style={{ width: 'auto' }} id="routine" />
              <label htmlFor="routine" style={{ ...s.label, cursor: 'pointer' }}>Daily routine goal</label>
            </div>
            {form.is_routine && (
              <div style={s.field}>
                <label style={s.label}>Routine Time</label>
                <input type="time" value={form.routine_time} onChange={e => setForm(f => ({ ...f, routine_time: e.target.value }))} />
              </div>
            )}
          </div>
          <div style={s.formActions}>
            <button type="button" onClick={() => setShowForm(false)} style={s.cancelBtn}>Cancel</button>
            <button type="submit" disabled={saving} style={s.primaryBtn}>
              {saving ? 'Saving...' : editGoal ? 'Save Changes' : 'Create Goal'}
            </button>
          </div>
        </form>
      )}

      {/* Filter tabs */}
      <div style={s.filters}>
        {['Active', 'Achieved', 'Paused', 'Dropped', 'all'].map(f => (
          <button key={f} onClick={() => setFilter(f)} style={{ ...s.filterBtn, ...(filter === f ? s.filterActive : {}) }}>
            {f === 'all' ? 'All' : f}
          </button>
        ))}
        <span style={s.filterCount}>{filtered.length} goal{filtered.length !== 1 ? 's' : ''}</span>
      </div>

      {/* Goals list */}
      {filtered.length === 0 ? (
        <div style={s.empty}>No goals here yet.</div>
      ) : (
        <div style={s.list}>
          {filtered.map(goal => (
            <GoalCard
              key={goal.id}
              goal={goal}
              onEdit={() => openEdit(goal)}
              onDelete={() => handleDelete(goal.id)}
              onStatusChange={(status) => quickStatus(goal.id, status)}
            />
          ))}
        </div>
      )}
    </PageShell>
  )
}

function GoalCard({ goal, onEdit, onDelete, onStatusChange }) {
  const color = STATUS_COLOR[goal.status] || 'var(--muted)'

  return (
    <div style={s.card}>
      <div style={s.cardTop}>
        {/* Streak bar */}
        {goal.streak > 0 && (
          <div style={s.streakBadge}>🔥 {goal.streak}d streak</div>
        )}
        <div style={s.cardMeta}>
          <span style={{ ...s.statusDot, backgroundColor: color }} />
          <span style={{ ...s.statusLabel, color }}>{goal.status}</span>
          {goal.category && <span style={s.categoryChip}>{goal.category}</span>}
          {goal.is_routine && <span style={s.routineBadge}>routine</span>}
          {goal.target_date && <span style={s.dateChip}>📅 {goal.target_date}</span>}
        </div>
        <div style={s.cardActions}>
          <button onClick={onEdit} style={s.iconBtn} title="Edit">✎</button>
          <button onClick={onDelete} style={{ ...s.iconBtn, color: 'var(--red)' }} title="Delete">✕</button>
        </div>
      </div>

      <h3 style={s.cardTitle}>{goal.title}</h3>
      {goal.description && <p style={s.cardDesc}>{goal.description}</p>}

      {/* Quick status toggle */}
      <div style={s.quickStatus}>
        {goal.status !== 'Achieved' && (
          <button onClick={() => onStatusChange('Achieved')} style={s.quickBtn}>Mark achieved ✓</button>
        )}
        {goal.status !== 'Active' && (
          <button onClick={() => onStatusChange('Active')} style={s.quickBtn}>Set active</button>
        )}
      </div>
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
  cancelBtn: {
    backgroundColor: 'transparent', color: 'var(--muted)', border: '1px solid var(--border)',
    borderRadius: 6, padding: '8px 18px', fontSize: '0.82rem', cursor: 'pointer', fontFamily: 'inherit',
  },
  form: {
    backgroundColor: 'var(--surface)', border: '1px solid var(--amber)', borderRadius: 10,
    padding: '20px', marginBottom: 24,
  },
  formTitle: { fontSize: '0.85rem', fontWeight: 600, color: 'var(--amber)', marginBottom: 16 },
  formGrid: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 },
  field: { display: 'flex', flexDirection: 'column', gap: 4 },
  label: { fontSize: '0.72rem', fontFamily: "'JetBrains Mono', monospace", color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.04em' },
  formActions: { marginTop: 16, display: 'flex', justifyContent: 'flex-end', gap: 10 },
  filters: { display: 'flex', gap: 6, marginBottom: 16, alignItems: 'center', flexWrap: 'wrap' },
  filterBtn: {
    backgroundColor: 'var(--surface)', border: '1px solid var(--border)', color: 'var(--muted)',
    borderRadius: 20, padding: '4px 14px', fontSize: '0.78rem', cursor: 'pointer', fontFamily: 'inherit',
  },
  filterActive: { backgroundColor: 'var(--amber-dim)', borderColor: 'var(--amber)', color: 'var(--amber-bright)' },
  filterCount: { marginLeft: 'auto', fontSize: '0.7rem', color: 'var(--muted)', fontFamily: "'JetBrains Mono', monospace" },
  list: { display: 'flex', flexDirection: 'column', gap: 10 },
  empty: { padding: '40px 0', color: 'var(--muted)', fontSize: '0.85rem', textAlign: 'center', fontFamily: "'JetBrains Mono', monospace" },
  card: {
    backgroundColor: 'var(--surface)', border: '1px solid var(--border)',
    borderRadius: 10, padding: '16px 18px',
  },
  cardTop: { display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8, flexWrap: 'wrap' },
  streakBadge: {
    fontSize: '0.72rem', fontFamily: "'JetBrains Mono', monospace",
    backgroundColor: 'rgba(245, 158, 11, 0.2)', border: '1px solid var(--amber)',
    color: 'var(--amber)', borderRadius: 10, padding: '2px 8px',
  },
  cardMeta: { display: 'flex', alignItems: 'center', gap: 6, flex: 1, flexWrap: 'wrap' },
  statusDot: { width: 7, height: 7, borderRadius: '50%', flexShrink: 0 },
  statusLabel: { fontSize: '0.72rem', fontFamily: "'JetBrains Mono', monospace", fontWeight: 600 },
  categoryChip: {
    fontSize: '0.68rem', fontFamily: "'JetBrains Mono', monospace", color: 'var(--muted)',
    backgroundColor: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 4, padding: '1px 6px',
  },
  routineBadge: {
    fontSize: '0.65rem', fontFamily: "'JetBrains Mono', monospace", color: 'var(--amber)',
    backgroundColor: 'var(--amber-dim)', borderRadius: 4, padding: '1px 6px',
  },
  dateChip: {
    fontSize: '0.68rem', fontFamily: "'JetBrains Mono', monospace", color: 'var(--muted)',
  },
  cardActions: { display: 'flex', gap: 6, marginLeft: 'auto' },
  iconBtn: {
    background: 'none', border: 'none', color: 'var(--muted)', cursor: 'pointer',
    fontSize: '0.9rem', padding: '2px 6px', borderRadius: 4,
  },
  cardTitle: { fontSize: '1rem', fontWeight: 600, color: '#e6edf3', marginBottom: 4 },
  cardDesc: { fontSize: '0.83rem', color: 'var(--muted)', lineHeight: 1.5, marginBottom: 10 },
  quickStatus: { display: 'flex', gap: 8, marginTop: 10 },
  quickBtn: {
    fontSize: '0.72rem', backgroundColor: 'transparent', border: '1px solid var(--border)',
    color: 'var(--muted)', borderRadius: 4, padding: '3px 10px', cursor: 'pointer',
    fontFamily: 'inherit', transition: 'border-color 0.15s, color 0.15s',
  },
}
