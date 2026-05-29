'use client'

import { useState } from 'react'
import NavBar from '../../components/NavBar'

export default function AnalyseRequestPage() {
  const [code, setCode] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await fetch('/api/analyse-access', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: code.trim() }),
      })
      if (res.ok) {
        window.location.href = '/analyse'
      } else {
        const data = await res.json()
        setError(data.error ?? 'Invalid access code.')
      }
    } catch {
      setError('Something went wrong. Try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <NavBar />
      <section style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '160px 48px 80px',
        textAlign: 'center',
      }}>

        <span style={{
          fontFamily: 'Geist Mono, monospace',
          fontSize: 11,
          letterSpacing: '0.16em',
          textTransform: 'uppercase',
          color: 'var(--ink)',
          opacity: 0.5,
          display: 'block',
          marginBottom: 24,
        }}>
          Restricted access
        </span>

        <h1 style={{
          fontFamily: '"SF Pro Display", -apple-system, BlinkMacSystemFont, system-ui, sans-serif',
          fontWeight: 100,
          fontSize: 'clamp(32px, 4vw, 52px)',
          letterSpacing: '0.03em',
          lineHeight: 1.1,
          marginBottom: 20,
          maxWidth: 540,
        }}>
          Research tool access
        </h1>

        <p style={{
          fontSize: 17,
          fontWeight: 300,
          color: 'var(--ink)',
          lineHeight: 1.75,
          maxWidth: 420,
          marginBottom: 48,
          opacity: 0.7,
        }}>
          This tool is available to approved research partners. Enter your access code below, or{' '}
          <a href="mailto:godwinyampoi449@gmail.com" style={{ color: 'var(--ink)', textDecoration: 'underline', textUnderlineOffset: 3 }}>
            contact us
          </a>{' '}
          to request access.
        </p>

        <form onSubmit={submit} style={{ width: '100%', maxWidth: 380 }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <input
              type="text"
              placeholder="Access code"
              value={code}
              onChange={e => setCode(e.target.value)}
              autoComplete="off"
              spellCheck={false}
              style={{
                fontFamily: 'Geist Mono, monospace',
                fontSize: 14,
                letterSpacing: '0.1em',
                background: 'rgba(255,255,255,0.05)',
                border: '1px solid var(--hairline)',
                borderRadius: 6,
                color: 'var(--ink)',
                padding: '14px 18px',
                outline: 'none',
                width: '100%',
                transition: 'border-color 0.15s',
              }}
              onFocus={e => (e.target.style.borderColor = 'rgba(255,255,255,0.35)')}
              onBlur={e => (e.target.style.borderColor = 'var(--hairline)')}
            />

            {error && (
              <p style={{
                fontFamily: 'Geist Mono, monospace',
                fontSize: 12,
                letterSpacing: '0.08em',
                color: '#ff6b6b',
                textAlign: 'left',
                margin: 0,
              }}>
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading || !code.trim()}
              style={{
                fontFamily: 'Geist Mono, monospace',
                fontSize: 11,
                letterSpacing: '0.14em',
                textTransform: 'uppercase',
                background: '#FFFFFF',
                color: '#000000',
                border: 'none',
                borderRadius: 999,
                padding: '12px 24px',
                cursor: loading || !code.trim() ? 'not-allowed' : 'pointer',
                opacity: loading || !code.trim() ? 0.45 : 1,
                transition: 'opacity 0.15s',
              }}
            >
              {loading ? 'Checking…' : 'Enter →'}
            </button>
          </div>
        </form>

      </section>
    </>
  )
}
