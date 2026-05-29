import { APPROACH } from '@/content/home'

export default function ApproachSection() {
  return (
    <section style={{ padding: '120px 0 80px', borderTop: '1px solid var(--hairline)' }}>
      <div className="wrap">

        <div style={{ marginBottom: 72 }}>
          <span style={{
            fontFamily: 'Geist Mono, monospace',
            fontSize: 11,
            letterSpacing: '0.16em',
            textTransform: 'uppercase',
            color: 'var(--teal)',
          }}>
            {APPROACH.label}
          </span>
          <h2 style={{
            fontFamily: 'Geist, sans-serif',
            fontWeight: 600,
            fontSize: 'clamp(28px, 4vw, 48px)',
            letterSpacing: '-0.03em',
            lineHeight: 1.1,
            marginTop: 16,
            maxWidth: 560,
          }}>
            {APPROACH.heading}
          </h2>
        </div>

        <div className="approach-grid">
          {APPROACH.columns.map(col => (
            <div key={col.n} className="approach-col">
              <span style={{
                fontFamily: 'Geist Mono, monospace',
                fontSize: 11,
                letterSpacing: '0.16em',
                color: 'var(--slate)',
                display: 'block',
                marginBottom: 24,
              }}>
                {col.n}
              </span>
              <h3 style={{
                fontFamily: 'Geist, sans-serif',
                fontWeight: 600,
                fontSize: 18,
                letterSpacing: '-0.02em',
                lineHeight: 1.2,
                marginBottom: 14,
              }}>
                {col.heading}
              </h3>
              <p style={{
                fontSize: 17,
                color: 'var(--ink)',
                lineHeight: 1.75,
              }}>
                {col.body}
              </p>
            </div>
          ))}
        </div>

      </div>
    </section>
  )
}
