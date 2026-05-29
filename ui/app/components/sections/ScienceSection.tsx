import { SCIENCE } from '@/content/home'

export default function ScienceSection() {
  return (
    <section style={{ padding: '100px 0', borderTop: '1px solid var(--hairline)' }}>
      <div className="wrap">

        <span style={{
          fontFamily: 'Geist Mono, monospace',
          fontSize: 11,
          letterSpacing: '0.16em',
          textTransform: 'uppercase',
          color: 'var(--teal)',
          display: 'block',
          marginBottom: 20,
        }}>
          {SCIENCE.label}
        </span>

        <h2 style={{
          fontFamily: 'Geist, sans-serif',
          fontWeight: 600,
          fontSize: 'clamp(36px, 5vw, 64px)',
          letterSpacing: '-0.04em',
          lineHeight: 1.0,
          marginBottom: 28,
        }}>
          {SCIENCE.heading}
        </h2>

        <p style={{
          fontSize: 17,
          color: 'var(--ink)',
          lineHeight: 1.75,
          maxWidth: 600,
          marginBottom: 72,
        }}>
          {SCIENCE.sub}
        </p>

        <div className="science-stats">
          {SCIENCE.stats.map(s => (
            <div key={s.label} style={{ borderTop: '1px solid var(--hairline)', paddingTop: 24 }}>
              <div style={{
                fontFamily: 'Geist, sans-serif',
                fontWeight: 600,
                fontSize: 'clamp(32px, 4vw, 52px)',
                letterSpacing: '-0.04em',
                lineHeight: 1.0,
                marginBottom: 8,
              }}>
                {s.value}
              </div>
              <div style={{
                fontFamily: 'Geist Mono, monospace',
                fontSize: 11,
                letterSpacing: '0.14em',
                textTransform: 'uppercase',
                color: 'var(--slate)',
              }}>
                {s.label}
              </div>
            </div>
          ))}
        </div>

      </div>
    </section>
  )
}
