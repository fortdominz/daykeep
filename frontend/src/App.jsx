import { BrowserRouter, Routes, Route, NavLink, useLocation, useNavigate } from 'react-router-dom'
import Dashboard from './components/Dashboard'
import Goals from './components/Goals'
import Tasks from './components/Tasks'
import Journal from './components/Journal'
import Analytics from './components/Analytics'
import ErrorBoundary from './components/ErrorBoundary'

function Sidebar() {
  const location = useLocation()
  const navigate = useNavigate()

  const navItems = [
    { to: '/',          label: 'Dashboard', icon: '⌂' },
    { to: '/tasks',     label: 'Tasks',     icon: '✓' },
    { to: '/goals',     label: 'Goals',     icon: '◎' },
    { to: '/journal',   label: 'Journal',   icon: '🖌' },
    { to: '/analytics', label: 'Analytics', icon: '~' },
  ]

  const canGoBack = location.pathname !== '/'

  return (
    <aside style={styles.sidebar}>
      {/* Logo */}
      <div style={styles.logo}>
        <span style={styles.logoMark}>DK</span>
        <div>
          <div style={styles.logoName}>DayKeep</div>
          <div style={styles.logoTagline}>keep your word</div>
        </div>
      </div>

      {/* Back button — shown on any page that isn't the dashboard */}
      {canGoBack && (
        <button onClick={() => navigate(-1)} style={styles.backBtn}>
          ← Back
        </button>
      )}

      {/* Nav */}
      <nav style={styles.nav}>
        {navItems.map(({ to, label, icon }) => {
          const active = to === '/' ? location.pathname === '/' : location.pathname.startsWith(to)
          return (
            <NavLink key={to} to={to} style={{ textDecoration: 'none' }}>
              <div style={{ ...styles.navItem, ...(active ? styles.navItemActive : {}) }}>
                <span style={styles.navIcon}>{icon}</span>
                <span>{label}</span>
                {active && <div style={styles.navIndicator} />}
              </div>
            </NavLink>
          )
        })}
      </nav>

      {/* Footer */}
      <div style={styles.sidebarFooter}>
        <div style={styles.footerLabel}>DayKeep</div>
        <div style={styles.footerSub}>keep your day. keep your word.</div>
      </div>
    </aside>
  )
}

function Layout({ children }) {
  return (
    <div style={styles.layout}>
      <Sidebar />
      <main style={styles.main}>
        {children}
      </main>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/"          element={<ErrorBoundary><Dashboard /></ErrorBoundary>} />
          <Route path="/tasks"     element={<ErrorBoundary><Tasks /></ErrorBoundary>} />
          <Route path="/goals"     element={<ErrorBoundary><Goals /></ErrorBoundary>} />
          <Route path="/journal"   element={<ErrorBoundary><Journal /></ErrorBoundary>} />
          <Route path="/analytics" element={<ErrorBoundary><Analytics /></ErrorBoundary>} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

const styles = {
  layout: {
    display: 'flex',
    minHeight: '100vh',
    width: '100%',
  },
  sidebar: {
    width: 220,
    minWidth: 220,
    backgroundColor: 'var(--surface)',
    borderRight: '1px solid var(--border)',
    display: 'flex',
    flexDirection: 'column',
    padding: '24px 0',
    position: 'sticky',
    top: 0,
    height: '100vh',
    overflowY: 'auto',
  },
  logo: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
    padding: '0 20px 20px',
    borderBottom: '1px solid var(--border)',
    marginBottom: 12,
  },
  logoMark: {
    width: 36,
    height: 36,
    backgroundColor: 'var(--amber)',
    color: '#0d1117',
    borderRadius: 8,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontWeight: 700,
    fontSize: '0.8rem',
    fontFamily: "'JetBrains Mono', monospace",
    flexShrink: 0,
  },
  logoName: {
    fontWeight: 700,
    fontSize: '0.95rem',
    color: '#e6edf3',
    letterSpacing: '-0.01em',
  },
  logoTagline: {
    fontSize: '0.65rem',
    color: 'var(--muted)',
    fontFamily: "'JetBrains Mono', monospace",
    letterSpacing: '0.04em',
  },
  backBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: 6,
    margin: '0 10px 8px',
    padding: '7px 12px',
    backgroundColor: 'transparent',
    border: '1px solid var(--border)',
    borderRadius: 6,
    color: 'var(--muted)',
    fontSize: '0.78rem',
    fontFamily: "'JetBrains Mono', monospace",
    cursor: 'pointer',
    transition: 'color 0.15s, border-color 0.15s',
    width: 'calc(100% - 20px)',
  },
  nav: {
    display: 'flex',
    flexDirection: 'column',
    gap: 2,
    padding: '0 10px',
    flex: 1,
  },
  navItem: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
    padding: '9px 12px',
    borderRadius: 6,
    color: 'var(--muted)',
    fontSize: '0.875rem',
    fontWeight: 500,
    position: 'relative',
    cursor: 'pointer',
    transition: 'color 0.15s, background-color 0.15s',
  },
  navItemActive: {
    backgroundColor: 'var(--amber-dim)',
    color: 'var(--amber-bright)',
  },
  navIcon: {
    fontSize: '0.85rem',
    width: 16,
    textAlign: 'center',
  },
  navIndicator: {
    position: 'absolute',
    right: 0,
    top: '50%',
    transform: 'translateY(-50%)',
    width: 3,
    height: 16,
    backgroundColor: 'var(--amber)',
    borderRadius: '3px 0 0 3px',
  },
  main: {
    flex: 1,
    overflowY: 'auto',
    backgroundColor: 'var(--bg)',
    minHeight: '100vh',
  },
  sidebarFooter: {
    padding: '20px',
    borderTop: '1px solid var(--border)',
    marginTop: 'auto',
  },
  footerLabel: {
    fontSize: '0.7rem',
    fontFamily: "'JetBrains Mono', monospace",
    color: 'var(--muted)',
  },
  footerSub: {
    fontSize: '0.65rem',
    color: 'var(--border)',
    marginTop: 2,
    fontFamily: "'JetBrains Mono', monospace",
  },
}
