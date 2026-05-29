'use client'
import { useState, useEffect } from 'react'
import NavBar from '../components/NavBar'
import FooterSection from '../components/sections/FooterSection'

const STORAGE_KEY = 'senebiclabs_contributor_waitlist'

function WaitlistForm() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [done, setDone]       = useState(false)
  const [error, setError]     = useState('')

  useEffect(() => {
    if (localStorage.getItem(STORAGE_KEY) === 'true') setDone(true)
  }, [])

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (loading) return
    setLoading(true)
    setError('')
    try {
      const res = await fetch('/api/waitlist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, type: 'contributor' }),
      })
      const data = await res.json()
      if (!data.ok) throw new Error(data.message ?? '')
      localStorage.setItem(STORAGE_KEY, 'true')
      setDone(true)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  if (done) return (
    <p style={{ fontSize: 16, color: 'var(--teal)', marginTop: 16 }}>You are on the list. We will be in touch.</p>
  )

  return (
    <form onSubmit={submit} style={{ display: 'flex', gap: 12, marginTop: 40, flexWrap: 'wrap', justifyContent: 'center' }}>
      <input
        type="email"
        className="mf-input"
        placeholder="your@email.com"
        value={email}
        onChange={e => setEmail(e.target.value)}
        required
        disabled={loading}
        style={{ width: 300, margin: 0 }}
      />
      <button className="mf-submit" type="submit" disabled={loading}>
        {loading ? 'Joining…' : 'Join the waitlist'}
      </button>
      {error && <p style={{ width: '100%', textAlign: 'center', fontSize: 14, color: 'var(--red, #e05)' }}>{error}</p>}
    </form>
  )
}

export default function ContributePage() {
  return (
    <>
      <NavBar active="contribute" />

      <section className="hero noise" style={{ padding: 'clamp(120px, 16vw, 180px) 0 clamp(80px, 12vw, 160px)', textAlign: 'center' }}>
        <div className="wrap">
          <span className="micro" style={{ marginBottom: 32, display: 'block' }}>For medical professionals</span>
          <h1 style={{
            fontFamily: 'Geist, sans-serif',
            fontWeight: 700,
            fontSize: 'clamp(52px, 8vw, 96px)',
            lineHeight: 1.0,
            letterSpacing: '-0.035em',
            textWrap: 'balance',
            marginBottom: 28,
          }}>
            Your clinical knowledge<br />becomes the ground truth<br />the model learns from.
          </h1>
          <p style={{ fontSize: 20, color: 'var(--ink)', lineHeight: 1.7, maxWidth: 580, margin: '0 auto' }}>
            We are building a programme where medical professionals contribute the data and judgment the model is trained on, and get paid for it. Not open yet.
          </p>
          <WaitlistForm />
        </div>
      </section>

      <FooterSection />
    </>
  )
}
