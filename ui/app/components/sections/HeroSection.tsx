import { HERO } from '@/content/home'

export default function HeroSection() {
  return (
    <section style={{
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      textAlign: 'center',
      padding: '0',
      paddingTop: '160px',
      paddingBottom: '80px',
    }}>

      <div style={{ marginBottom: 40 }}>
        <svg width="40" height="40" viewBox="0 0 26 26" fill="none" style={{ color: 'var(--teal)' }}>
          <circle cx="13" cy="13" r="11" stroke="currentColor" strokeWidth="1.6" fill="none"/>
          <path d="M 4 11 C 7 5 11 6 13 9.5 C 15 13 19 12 22 8"
                stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" fill="none"/>
          <path d="M 4 18 C 7 12 11 13 13 16.5 C 15 20 19 19 22 15"
                stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" fill="none"/>
        </svg>
      </div>

      <h1 style={{
        fontFamily: '"SF Pro Display", -apple-system, BlinkMacSystemFont, system-ui, sans-serif',
        fontWeight: 100,
        fontSize: 'clamp(36px, 5vw, 72px)',
        lineHeight: 1.06,
        letterSpacing: '0.04em',
        marginBottom: 32,
      } as React.CSSProperties}>
        {HERO.mission}
      </h1>

      <p style={{
        fontFamily: '"DM Sans", system-ui, sans-serif',
        fontWeight: 100,
        fontSize: 'clamp(18px, 1.8vw, 26px)',
        color: 'var(--ink)',
        lineHeight: 1.65,
        maxWidth: 800,
        marginBottom: 52,
      }}>
        {HERO.sub}
      </p>

      <div style={{ display: 'flex', gap: 40, alignItems: 'center', justifyContent: 'center' }}>
        <a href="/experts" className="iso-cta">Join as specialist →</a>
        <a href="/patients" className="iso-cta iso-cta--muted">For patients →</a>
      </div>

    </section>
  )
}
