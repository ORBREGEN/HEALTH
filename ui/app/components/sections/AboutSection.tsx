import { HERO } from '@/content/home'

export default function AboutSection() {
  return (
    <section style={{
      padding: '140px 0',
      borderTop: '1px solid var(--hairline)',
    }}>

      <div style={{ marginBottom: 80 }}>
        <span style={{
          fontFamily: 'Geist Mono, monospace',
          fontSize: 11,
          letterSpacing: '0.16em',
          textTransform: 'uppercase',
          color: 'var(--teal)',
          display: 'block',
          marginBottom: 40,
        }}>
          Who we are
        </span>

        <p style={{
          fontFamily: '"SF Pro Display", -apple-system, BlinkMacSystemFont, system-ui, sans-serif',
          fontWeight: 100,
          fontSize: 'clamp(32px, 4vw, 58px)',
          lineHeight: 1.3,
          letterSpacing: '0.02em',
          color: 'var(--ink)',
        } as React.CSSProperties}>
          {HERO.p1}
        </p>
      </div>

      <div style={{
        height: 1,
        background: 'var(--hairline)',
        marginBottom: 72,
      }} />

      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '0 6vw',
      }}>
        <p style={{
          fontFamily: '"DM Sans", system-ui, sans-serif',
          fontWeight: 100,
          fontSize: 20,
          lineHeight: 1.85,
          color: 'var(--ink)',
        }}>{HERO.p2}</p>
        <p style={{
          fontFamily: '"DM Sans", system-ui, sans-serif',
          fontWeight: 100,
          fontSize: 20,
          lineHeight: 1.85,
          color: 'var(--ink)',
        }}>{HERO.p3}</p>
      </div>

    </section>
  )
}
