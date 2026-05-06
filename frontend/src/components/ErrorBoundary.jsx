import { Component } from 'react'

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { error: null }
  }

  static getDerivedStateFromError(error) {
    return { error }
  }

  componentDidCatch(error, info) {
    console.error('DayKeep render error:', error, info)
  }

  render() {
    if (this.state.error) {
      return (
        <div style={{
          padding: '40px 36px',
          fontFamily: "'JetBrains Mono', monospace",
          color: '#ef4444',
          fontSize: '0.82rem',
        }}>
          <div style={{ marginBottom: 8, fontWeight: 700 }}>Something went wrong on this page.</div>
          <div style={{ color: '#6e7f94', marginBottom: 20 }}>{this.state.error.message}</div>
          <button
            onClick={() => this.setState({ error: null })}
            style={{
              background: 'none', border: '1px solid #ef4444', color: '#ef4444',
              borderRadius: 6, padding: '6px 14px', cursor: 'pointer',
              fontFamily: 'inherit', fontSize: '0.78rem',
            }}
          >
            Try again
          </button>
        </div>
      )
    }
    return this.props.children
  }
}
