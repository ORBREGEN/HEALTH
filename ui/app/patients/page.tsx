'use client'
import { useState, useEffect } from 'react'
import NavBar from '../components/NavBar'
import FooterSection from '../components/sections/FooterSection'
import Toast from '../components/ui/Toast'

function useLocation() {
  const [coords, setCoords] = useState<{ lat: number; lng: number } | null>(null)
  useEffect(() => {
    if (!navigator.geolocation) return
    navigator.geolocation.getCurrentPosition(
      pos => setCoords({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
      () => {},
      { timeout: 8000 }
    )
  }, [])
  return coords
}

const STORAGE_KEY = 'senebiclabs_patient_waitlist'

function WaitlistForm() {
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [done, setDone] = useState(false)

  useEffect(() => {
    if (localStorage.getItem(STORAGE_KEY) === 'true') setDone(true)
  }, [])
  const [error, setError]     = useState('')

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (loading) return
    setLoading(true)
    setError('')
    try {
      const res = await fetch('/api/waitlist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          type: 'patient',
          lat: location?.lat ?? null,
          lng: location?.lng ?? null,
        }),
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
    <p style={{ fontSize: 16, color: 'var(--teal)', marginTop: 16 }}>You are on the list. We will be in touch when we launch.</p>
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
      {error && <Toast message={error} onDismiss={() => setError('')} />}
    </form>
  )
}

export default function PatientsPage() {
  return (
    <>
      <NavBar active="patients" />

      <section className="hero noise" style={{ padding: 'clamp(120px, 16vw, 180px) 0 clamp(80px, 12vw, 160px)', textAlign: 'center' }}>
        <div className="wrap">
          <span className="micro" style={{ marginBottom: 32, display: 'block' }}>For patients</span>
          <h1 style={{
            fontFamily: 'Geist, sans-serif',
            fontWeight: 700,
            fontSize: 'clamp(52px, 8vw, 96px)',
            lineHeight: 1.0,
            letterSpacing: '-0.035em',
            textWrap: 'balance',
            marginBottom: 28,
          }}>
            Find the doctor who is right<br />for what you actually have.
          </h1>
          <p style={{ fontSize: 20, color: 'var(--ink)', lineHeight: 1.7, maxWidth: 580, margin: '0 auto' }}>
            Tell us your symptoms. We match you to the nearest suitable specialist, not whoever has a free slot, the one who is right for what you actually have. Launching soon.
          </p>
          <WaitlistForm />
          <p style={{ marginTop: 20, fontFamily: 'var(--font-mono, monospace)', fontSize: 11, color: 'var(--slate)', letterSpacing: '0.08em' }}>
            Senebiclabs does not provide medical advice. Specialist matching is informational only. Always consult a licensed medical professional.
          </p>
        </div>
      </section>

      <FooterSection />
    </>
  )
}
