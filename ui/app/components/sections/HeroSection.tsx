import { HERO } from '@/content/home'

export default function HeroSection() {
  return (
    <section className="hero-section" style={{
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      textAlign: 'center',
      paddingTop: '160px',
      paddingBottom: '80px',
    }}>
      <div className="wrap" style={{ width: '100%' }}>

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
          fontSize: 'clamp(17px, 1.8vw, 24px)',
          color: 'var(--ink)',
          lineHeight: 1.65,
          maxWidth: 700,
          marginBottom: 52,
          marginLeft: 'auto',
          marginRight: 'auto',
        }}>
          {HERO.sub}
        </p>

        <div style={{ display: 'flex', gap: 32, alignItems: 'center', justifyContent: 'center', flexWrap: 'wrap' }}>
          <a href="/experts" className="iso-cta">Join as specialist →</a>
          <a href="/patients" className="iso-cta iso-cta--muted">For patients →</a>
        </div>

      </div>
    </section>
  )
}
