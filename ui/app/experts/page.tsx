'use client'
import { useState, useEffect } from 'react'
import NavBar from '../components/NavBar'
import FooterSection from '../components/sections/FooterSection'

const BENEFITS = [
  {
    heading: 'Cases matched to your expertise',
    body: 'Every patient the platform sends you has been selected because their presentation fits your specific specialty. No random referrals. No consultations that go nowhere.',
  },
  {
    heading: 'Full picture before you start',
    body: 'Each case arrives with a structured summary — symptom history, duration, key flags, and relevant context. You start from a position of clarity, not catch-up.',
  },
  {
    heading: 'Patients beyond your geography',
    body: 'Patients anywhere can be matched to you through Senebiclabs. Your expertise reaches them without changing where or how you practice.',
  },
  {
    heading: 'You control your capacity',
    body: 'Set your availability on your terms. Accept as many or as few cases as you choose. Nothing is assigned to you without your explicit consent.',
  },
]

const HOW = [
  {
    n: '01',
    heading: 'Apply and get verified',
    body: 'Submit your credentials, licence number, specialty, and institution. Every application is reviewed personally and credentials are verified before anyone joins.',
  },
  {
    n: '02',
    heading: 'Your profile enters the network',
    body: 'Once verified, your specialty and location are factored into the matching engine. Patients whose presentation fits your expertise are routed to you.',
  },
  {
    n: '03',
    heading: 'Every referral arrives prepared',
    body: 'Each case comes with a full structured summary. You spend your time on clinical judgment, not piecing together history from scratch.',
  },
]

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

const STORAGE_KEY = 'senebiclabs_expert_applied'

function ApplicationForm() {
  const location = useLocation()
  const [form, setForm] = useState({ name: '', email: '', note: '' })
  const [agreedToTerms, setAgreedToTerms] = useState(false)
  const [loading, setLoading] = useState(false)
  const [done, setDone]       = useState(false)
  const [error, setError]     = useState('')

  useEffect(() => {
    if (localStorage.getItem(STORAGE_KEY) === 'true') setDone(true)
  }, [])

  const set = (k: keyof typeof form) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      setForm(f => ({ ...f, [k]: e.target.value }))

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (loading) return
    if (!agreedToTerms) {
      setError('Please confirm that you agree to the terms before submitting.')
      return
    }
    setLoading(true)
    setError('')
    try {
      const res = await fetch('/api/apply', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...form,
          agreed_to_terms: true,
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
    <div className="mf-success" style={{ maxWidth: 640, margin: '0 auto' }}>
      <svg className="mf-success-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <polyline points="20 6 9 17 4 12" />
      </svg>
      <div>
        <h4>You are on the list.</h4>
        <p>We will verify your credentials and reach out when the app is ready to launch.</p>
      </div>
    </div>
  )

  return (
    <form className="mf-form" style={{ maxWidth: 560, margin: '0 auto' }} onSubmit={submit}>
      <div className="mf-row cols-2">
        <div className="mf-field">
          <label className="mf-label">Full name</label>
          <input className="mf-input" type="text" placeholder="Dr. Your Name" value={form.name} onChange={set('name')} required disabled={loading} />
        </div>
        <div className="mf-field">
          <label className="mf-label">Email</label>
          <input className="mf-input" type="email" placeholder="you@hospital.org" value={form.email} onChange={set('email')} required disabled={loading} />
        </div>
      </div>
      <div className="mf-row cols-1">
        <div className="mf-field">
          <label className="mf-label">
            Anything you want us to know
            <span style={{ color: 'var(--slate-2)', fontWeight: 400 }}> — optional</span>
          </label>
          <textarea className="mf-textarea" placeholder="Specialty, institution, or anything else…" value={form.note} onChange={set('note')} disabled={loading} />
        </div>
      </div>
      <div className="mf-footer" style={{ flexDirection: 'column', alignItems: 'stretch', gap: 16 }}>
        <label className="mf-terms-label">
          <input
            type="checkbox"
            checked={agreedToTerms}
            onChange={e => setAgreedToTerms(e.target.checked)}
            disabled={loading}
            className="mf-terms-check"
          />
          <span>
            I confirm that I am a licensed medical professional and I consent to Senebiclabs
            contacting me when the mobile app launches.
          </span>
        </label>
        <button className="mf-submit" type="submit" disabled={loading || !agreedToTerms} style={{ width: '100%' }}>
          {loading ? 'Submitting…' : 'Reserve your place →'}
        </button>
        <span className="mf-note" style={{ textAlign: 'center' }}>
          Every application is reviewed personally. We verify credentials before the app launches.
        </span>
      </div>
      {error && <p className="mf-error" style={{ textAlign: 'center' }}>{error}</p>}
    </form>
  )
}

export default function ExpertsPage() {
  return (
    <>
      <NavBar active="experts" />

      {/* Hero */}
      <section className="hero noise" style={{ padding: '180px 0 160px', textAlign: 'center' }}>
        <div className="wrap">
          <span className="micro" style={{ marginBottom: 32, display: 'block' }}>Specialist network · Pre-launch</span>
          <h1 style={{
            fontFamily: '"SF Pro Display", -apple-system, BlinkMacSystemFont, system-ui, sans-serif',
            fontWeight: 100,
            fontSize: 'clamp(48px, 7vw, 88px)',
            lineHeight: 1.05,
            letterSpacing: '0.02em',
            textWrap: 'balance',
            marginBottom: 28,
          }}>
            See only the cases<br />that fit your expertise.
          </h1>
          <p style={{ fontSize: 20, color: 'var(--ink)', lineHeight: 1.75, maxWidth: 560, margin: '0 auto 40px' }}>
            We are building the mobile app. Submit your credentials now and we will verify them before launch. When the app goes live, you will be among the first specialists activated on the network.
          </p>
          <a href="#apply" className="nav-join-cta" style={{ fontSize: 13, padding: '12px 28px' }}>
            Reserve your place →
          </a>
        </div>
      </section>

      {/* Benefits */}
      <section style={{ padding: '100px 0', borderTop: '1px solid var(--hairline)' }}>
        <div className="wrap">
          <span className="micro" style={{ display: 'block', marginBottom: 20 }}>What you get</span>
          <h2 style={{
            fontFamily: 'Geist, sans-serif',
            fontWeight: 600,
            fontSize: 'clamp(30px, 4vw, 52px)',
            letterSpacing: '-0.025em',
            lineHeight: 1.08,
            marginBottom: 64,
            textWrap: 'balance',
          }}>
            Better cases. Less wasted time.
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 2, background: 'var(--hairline)', border: '1px solid var(--hairline)', borderRadius: 16, overflow: 'hidden' }}>
            {BENEFITS.map(b => (
              <div key={b.heading}
                style={{ background: 'var(--navy)', padding: '52px 48px', transition: 'background 0.25s' }}
                onMouseEnter={e => (e.currentTarget.style.background = 'var(--navy-2)')}
                onMouseLeave={e => (e.currentTarget.style.background = 'var(--navy)')}>
                <h3 style={{ fontFamily: 'Geist, sans-serif', fontSize: 22, fontWeight: 500, letterSpacing: '-0.01em', lineHeight: 1.2, marginBottom: 16 }}>{b.heading}</h3>
                <p style={{ fontSize: 17, color: 'var(--ink)', lineHeight: 1.7 }}>{b.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="philosophy" style={{ paddingTop: 100 }}>
        <div className="wrap">
          <span className="micro">How it works</span>
          <p className="philosophy-statement" style={{ marginTop: 20 }}>
            Apply. Get verified.<br />
            <em style={{ color: 'var(--teal)' }}>Start seeing the right patients.</em>
          </p>
          <div className="philosophy-pillars">
            {HOW.map(step => (
              <div className="pillar" key={step.n}>
                <div className="pn">{step.n}</div>
                <h3>{step.heading}</h3>
                <p>{step.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Application form, centred */}
      <section id="apply" style={{ padding: '120px 0', borderTop: '1px solid var(--hairline)', textAlign: 'center' }}>
        <div className="wrap">
          <span className="micro" style={{ display: 'block', marginBottom: 24 }}>Apply to join</span>
          <h2 style={{
            fontFamily: 'Geist, sans-serif',
            fontWeight: 600,
            fontSize: 'clamp(32px, 4.5vw, 56px)',
            letterSpacing: '-0.028em',
            lineHeight: 1.06,
            marginBottom: 16,
            textWrap: 'balance',
          }}>
            Reserve your place before we launch.
          </h2>
          <p style={{ fontSize: 17, color: 'var(--slate)', lineHeight: 1.7, maxWidth: 520, margin: '0 auto 56px' }}>
            Submit your credentials now. We review every application personally and verify them before the app launches. When it does, your profile goes live immediately.
          </p>
          <ApplicationForm />
        </div>
      </section>

      <FooterSection />
    </>
  )
}
