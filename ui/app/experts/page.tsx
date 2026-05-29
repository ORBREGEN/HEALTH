'use client'
import { useState, useEffect } from 'react'
import NavBar from '../components/NavBar'
import FooterSection from '../components/sections/FooterSection'

const SPECIALTIES = [
  'Pulmonology',
  'Respiratory medicine',
  'Allergy & immunology',
  'Critical care / intensive care',
  'Sleep medicine',
  'Thoracic surgery',
  'Paediatric pulmonology',
  'General practice (respiratory focus)',
  'Other',
]

const EXPERIENCE = [
  'Less than 2 years',
  '2–5 years',
  '5–10 years',
  '10–20 years',
  'More than 20 years',
]

const BENEFITS = [
  {
    heading: 'Only cases that fit you',
    body: 'Every patient referred to you has been matched based on their symptoms and your specialty. No random referrals. No wasted consultations.',
  },
  {
    heading: 'Full context before you start',
    body: 'Each case arrives with a structured summary already prepared, symptom history, key flags, relevant background. You start further along.',
  },
  {
    heading: 'Reach patients beyond your postcode',
    body: 'Patients find you through Senebiclabs regardless of where they are. You expand your reach without changing how or where you practice.',
  },
  {
    heading: 'You set the terms',
    body: 'You control your availability. Take on as many or as few cases as you want. Nothing is assigned without your consent.',
  },
]

const HOW = [
  {
    n: '01',
    heading: 'Apply and get verified',
    body: 'Submit your credentials, licence number, specialty, and institution. We verify every doctor personally before they join.',
  },
  {
    n: '02',
    heading: 'Your profile goes live',
    body: 'Once approved, your specialty and location are part of the matching engine. Patients near you whose presentation fits your expertise are routed to you.',
  },
  {
    n: '03',
    heading: 'See prepared cases',
    body: 'Every referral arrives with a full case summary. You spend your time on clinical judgment, not catching up on history.',
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

function ApplicationForm() {
  const location = useLocation()
  const [form, setForm] = useState({
    name: '', email: '', specialty: '', institution: '',
    country: '', license: '', experience: '', note: '',
  })
  const [loading, setLoading] = useState(false)
  const [done, setDone]       = useState(false)
  const [error, setError]     = useState('')

  const set = (k: keyof typeof form) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
      setForm(f => ({ ...f, [k]: e.target.value }))

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (loading) return
    setLoading(true)
    setError('')
    try {
      const res = await fetch('/api/apply', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...form,
          type: 'expert',
          lat: location?.lat ?? null,
          lng: location?.lng ?? null,
        }),
      })
      const data = await res.json()
      if (!data.ok) throw new Error(data.message ?? '')
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
        <h4>Application received.</h4>
        <p>We will review your credentials and be in touch within 5 business days.</p>
      </div>
    </div>
  )

  return (
    <form className="mf-form" style={{ maxWidth: 760, margin: '0 auto' }} onSubmit={submit}>
      <div className="mf-row cols-2">
        <div className="mf-field">
          <label className="mf-label">Full name</label>
          <input className="mf-input" type="text" placeholder="Dr. Your Name" value={form.name} onChange={set('name')} required disabled={loading} />
        </div>
        <div className="mf-field">
          <label className="mf-label">Professional email</label>
          <input className="mf-input" type="email" placeholder="you@hospital.org" value={form.email} onChange={set('email')} required disabled={loading} />
        </div>
      </div>
      <div className="mf-row cols-2">
        <div className="mf-field">
          <label className="mf-label">Specialty</label>
          <select className="mf-select" value={form.specialty} onChange={set('specialty')} required disabled={loading}>
            <option value="" disabled>Select specialty</option>
            {SPECIALTIES.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
        <div className="mf-field">
          <label className="mf-label">Institution / Hospital</label>
          <input className="mf-input" type="text" placeholder="Where you practice" value={form.institution} onChange={set('institution')} required disabled={loading} />
        </div>
      </div>
      <div className="mf-row cols-2">
        <div className="mf-field">
          <label className="mf-label">Country</label>
          <input className="mf-input" type="text" placeholder="Country" value={form.country} onChange={set('country')} required disabled={loading} />
        </div>
        <div className="mf-field">
          <label className="mf-label">Medical licence number</label>
          <input className="mf-input" type="text" placeholder="For credential verification" value={form.license} onChange={set('license')} required disabled={loading} />
        </div>
      </div>
      <div className="mf-row cols-1">
        <div className="mf-field">
          <label className="mf-label">Years of experience</label>
          <select className="mf-select" value={form.experience} onChange={set('experience')} required disabled={loading}>
            <option value="" disabled>Select range</option>
            {EXPERIENCE.map(ex => <option key={ex} value={ex}>{ex}</option>)}
          </select>
        </div>
      </div>
      <div className="mf-row cols-1">
        <div className="mf-field">
          <label className="mf-label">
            Anything else you want us to know
            <span style={{ color: 'var(--slate-2)', fontWeight: 400 }}>, optional</span>
          </label>
          <textarea className="mf-textarea" placeholder="Research focus, clinical interests, or why you want to join…" value={form.note} onChange={set('note')} disabled={loading} />
        </div>
      </div>
      <div className="mf-footer" style={{ flexDirection: 'column', alignItems: 'center', gap: 12 }}>
        <button className="mf-submit" type="submit" disabled={loading} style={{ width: '100%' }}>
          {loading ? 'Submitting…' : 'Submit application'}
        </button>
        <span className="mf-note" style={{ textAlign: 'center' }}>
          Every application is reviewed personally. We will be in touch within 5 business days.
        </span>
        <p style={{ margin: 0, fontFamily: 'var(--font-mono, monospace)', fontSize: 11, color: 'var(--slate)', letterSpacing: '0.08em', textAlign: 'center' }}>
          Senebiclabs is a research and matching platform. Clinical decisions remain the sole responsibility of the treating physician.
        </p>
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
          <span className="micro" style={{ marginBottom: 32, display: 'block' }}>For respiratory specialists</span>
          <h1 style={{
            fontFamily: 'Geist, sans-serif',
            fontWeight: 700,
            fontSize: 'clamp(52px, 8vw, 96px)',
            lineHeight: 1.0,
            letterSpacing: '-0.035em',
            textWrap: 'balance',
            marginBottom: 28,
          }}>
            The patients who need you<br />most can&apos;t find you.
          </h1>
          <p style={{ fontSize: 22, color: 'var(--ink)', lineHeight: 1.7, maxWidth: 600, margin: '0 auto' }}>
            Senebiclabs matches patients to the nearest suitable specialist based on what they actually have. Join the network, every case that reaches you already fits your expertise.
          </p>
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
            Join the specialist network.
          </h2>
          <p style={{ fontSize: 17, color: 'var(--slate)', lineHeight: 1.7, maxWidth: 520, margin: '0 auto 56px' }}>
            We verify every doctor before they join. This is a curated network, not a directory. Every application is reviewed personally.
          </p>
          <ApplicationForm />
        </div>
      </section>

      <FooterSection />
    </>
  )
}
