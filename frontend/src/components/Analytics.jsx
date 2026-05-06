import { useState, useEffect } from 'react'
import { api } from '../api'

export default function Analytics() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getAnalytics().then(d => { setData(d); setLoading(false) }).catch(console.error)
  }, [])

  if (loading) return <PageShell><div style={s.empty}>Loading analytics...</div></PageShell>
  if (!data)   return <PageShell><div style={s.empty}>No data yet.</div></PageShell>

  const completionPct = data.overall_rate
  const fillWidth = `${Math.min(completionPct, 100)}%`

  return (
    <PageShell>
      <div style={s.header}>
        <h1 style={s.pageTitle}>Analytics</h1>
        <div style={s.exportRow}>
          <a href="/api/export/tasks" style={s.exportBtn} download>↓ Tasks CSV</a>
          <a href="/api/export/goals" style={s.exportBtn} download>↓ Goals CSV</a>
        </div>
      </div>

      {/* Top stat grid */}
      <div style={s.statGrid}>
        <StatBlock label="Overall Completion" value={`${completionPct}%`} accent />
        <StatBlock label="Total Tasks" value={data.total_tasks} />
        <StatBlock label="Complete" value={data.completed} color="var(--green)" />
        <StatBlock label="Incomplete" value={data.incomplete} color="var(--red)" />
        <StatBlock label="Skipped" value={data.skipped} color="var(--muted)" />
        <StatBlock label="Postponed" value={data.postponed} color="var(--amber)" />
        <StatBlock label="Abandoned" value={data.abandoned} color="var(--red)" />
        <StatBlock label="Journal Entries" value={data.journal_count} />
      </div>

      {/* Progress bar */}
      <div style={s.section}>
        <div style={s.sectionTitle}>Completion Rate — All Time</div>
        <div style={s.barWrap}>
          <div style={s.barTrack}>
            <div style={{ ...s.barFill, width: fillWidth }} />
          </div>
          <span style={s.barLabel}>{completionPct}%</span>
        </div>
      </div>

      {/* Goals summary */}
      <div style={s.twoCol}>
        <div style={s.card}>
          <div style={s.cardTitle}>Goal Overview</div>
          <div style={s.cardRows}>
            <Row label="Total Goals" value={data.total_goals} />
            <Row label="Active" value={data.active_goals} color="var(--blue)" />
            <Row label="Achieved" value={data.achieved_goals} color="var(--green)" />
          </div>
        </div>

        <div style={s.card}>
          <div style={s.cardTitle}>Peak Productivity</div>
          <div style={s.peakDay}>{data.best_day}</div>
          <div style={s.peakLabel}>most completions on this day</div>
        </div>
      </div>

      {/* Streak leaderboard */}
      {data.goals_with_streaks.length > 0 && (
        <div style={s.section}>
          <div style={s.sectionTitle}>🔥 Active Streaks</div>
          <div style={s.streakList}>
            {data.goals_with_streaks.slice(0, 10).map((goal, i) => (
              <div key={goal.id} style={s.streakRow}>
                <span style={s.streakRank}>#{i + 1}</span>
                <span style={s.streakName}>{goal.title}</span>
                <div style={s.streakBarWrap}>
                  <div style={{ ...s.streakBarFill, width: `${Math.min(goal.streak * 5, 100)}%` }} />
                </div>
                <span style={s.streakCount}>{goal.streak}d</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Task status breakdown visual */}
      <div style={s.section}>
        <div style={s.sectionTitle}>Task Status Breakdown</div>
        <div style={s.breakdown}>
          {[
            { label: 'Complete',   value: data.completed,   color: 'var(--green)' },
            { label: 'Incomplete', value: data.incomplete,  color: 'var(--red)' },
            { label: 'Skipped',    value: data.skipped,     color: 'var(--muted)' },
            { label: 'Postponed',  value: data.postponed,   color: 'var(--amber)' },
            { label: 'Abandoned',  value: data.abandoned,   color: '#ef4444cc' },
            { label: 'Planned',    value: data.planned,     color: 'var(--blue)' },
          ].map(({ label, value, color }) => {
            const pct = data.total_tasks > 0 ? ((value / data.total_tasks) * 100).toFixed(1) : 0
            return (
              <div key={label} style={s.breakdownRow}>
                <span style={s.breakdownLabel}>{label}</span>
                <div style={s.breakdownTrack}>
                  <div style={{ ...s.breakdownFill, width: `${pct}%`, backgroundColor: color }} />
                </div>
                <span style={{ ...s.breakdownPct, color }}>{pct}%</span>
                <span style={s.breakdownCount}>{value}</span>
              </div>
            )
          })}
        </div>
      </div>
    </PageShell>
  )
}

function StatBlock({ label, value, accent, color }) {
  return (
    <div style={{ ...s.statBlock, ...(accent ? s.statAccent : {}) }}>
      <div style={{ ...s.statValue, color: accent ? 'var(--amber)' : color || '#e6edf3' }}>{value}</div>
      <div style={s.statLabel}>{label}</div>
    </div>
  )
}

function Row({ label, value, color }) {
  return (
    <div style={s.row}>
      <span style={s.rowLabel}>{label}</span>
      <span style={{ ...s.rowValue, color: color || 'var(--text)' }}>{value}</span>
    </div>
  )
}

function PageShell({ children }) {
  return <div style={s.page}>{children}</div>
}

const s = {
  page: { padding: '32px 36px', maxWidth: 860, animation: 'fadeIn 0.2s ease' },
  header: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 },
  pageTitle: { fontSize: '1.8rem', fontWeight: 700, color: '#e6edf3', lineHeight: 1.1 },
  exportRow: { display: 'flex', gap: 10 },
  exportBtn: {
    backgroundColor: 'var(--surface)', border: '1px solid var(--border)', color: 'var(--muted)',
    borderRadius: 6, padding: '6px 14px', fontSize: '0.78rem', textDecoration: 'none',
    fontFamily: "'JetBrains Mono', monospace', cursor: 'pointer",
  },
  statGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(100px, 1fr))', gap: 10, marginBottom: 24 },
  statBlock: {
    backgroundColor: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 8,
    padding: '14px', textAlign: 'center',
  },
  statAccent: { borderColor: 'var(--amber)', backgroundColor: 'var(--amber-dim)' },
  statValue: { fontSize: '1.5rem', fontWeight: 700, fontFamily: "'JetBrains Mono', monospace", lineHeight: 1 },
  statLabel: { fontSize: '0.65rem', color: 'var(--muted)', marginTop: 4, textTransform: 'uppercase', letterSpacing: '0.05em' },
  section: { marginBottom: 24 },
  sectionTitle: {
    fontSize: '0.72rem', fontFamily: "'JetBrains Mono', monospace", color: 'var(--muted)',
    textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 12,
    paddingBottom: 8, borderBottom: '1px solid var(--border)',
  },
  barWrap: { display: 'flex', alignItems: 'center', gap: 12 },
  barTrack: { flex: 1, height: 8, backgroundColor: 'var(--surface-2)', borderRadius: 4, overflow: 'hidden' },
  barFill: { height: '100%', backgroundColor: 'var(--amber)', borderRadius: 4, transition: 'width 0.6s ease' },
  barLabel: { fontSize: '0.8rem', fontFamily: "'JetBrains Mono', monospace", color: 'var(--amber)', minWidth: 40, textAlign: 'right' },
  twoCol: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, marginBottom: 24 },
  card: { backgroundColor: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 10, padding: '16px 18px' },
  cardTitle: { fontSize: '0.72rem', fontFamily: "'JetBrains Mono', monospace", color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 14 },
  cardRows: { display: 'flex', flexDirection: 'column', gap: 8 },
  row: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  rowLabel: { fontSize: '0.82rem', color: 'var(--muted)' },
  rowValue: { fontSize: '1rem', fontWeight: 700, fontFamily: "'JetBrains Mono', monospace" },
  peakDay: { fontSize: '1.6rem', fontWeight: 700, color: 'var(--amber)', marginBottom: 4 },
  peakLabel: { fontSize: '0.72rem', color: 'var(--muted)', fontFamily: "'JetBrains Mono', monospace" },
  streakList: { display: 'flex', flexDirection: 'column', gap: 8 },
  streakRow: { display: 'flex', alignItems: 'center', gap: 10 },
  streakRank: { fontSize: '0.68rem', fontFamily: "'JetBrains Mono', monospace", color: 'var(--muted)', minWidth: 24 },
  streakName: { fontSize: '0.83rem', color: 'var(--text)', flex: 1, minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' },
  streakBarWrap: { width: 120, height: 6, backgroundColor: 'var(--surface-2)', borderRadius: 3, overflow: 'hidden', flexShrink: 0 },
  streakBarFill: { height: '100%', backgroundColor: 'var(--amber)', borderRadius: 3, transition: 'width 0.4s ease' },
  streakCount: { fontSize: '0.72rem', fontFamily: "'JetBrains Mono', monospace", color: 'var(--amber)', minWidth: 28, textAlign: 'right' },
  breakdown: { display: 'flex', flexDirection: 'column', gap: 8 },
  breakdownRow: { display: 'flex', alignItems: 'center', gap: 10 },
  breakdownLabel: { fontSize: '0.75rem', color: 'var(--muted)', width: 80, flexShrink: 0 },
  breakdownTrack: { flex: 1, height: 6, backgroundColor: 'var(--surface-2)', borderRadius: 3, overflow: 'hidden' },
  breakdownFill: { height: '100%', borderRadius: 3, transition: 'width 0.4s ease', minWidth: 2 },
  breakdownPct: { fontSize: '0.7rem', fontFamily: "'JetBrains Mono', monospace", width: 38, textAlign: 'right' },
  breakdownCount: { fontSize: '0.7rem', fontFamily: "'JetBrains Mono', monospace", color: 'var(--muted)', width: 28, textAlign: 'right' },
  empty: { padding: '48px 0', color: 'var(--muted)', fontSize: '0.85rem', textAlign: 'center' },
}
