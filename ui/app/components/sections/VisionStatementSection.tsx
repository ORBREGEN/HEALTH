import { VISION_STATEMENT } from '@/content/home'

export default function VisionStatementSection() {
  return (
    <section style={{ padding: '140px 0', borderTop: '1px solid var(--hairline)' }}>
      <div className="wrap" style={{ maxWidth: 800 }}>

        <h2 style={{
          fontFamily: 'Geist, sans-serif',
          fontWeight: 700,
          fontSize: 'clamp(36px, 5vw, 64px)',
          letterSpacing: '-0.04em',
          lineHeight: 1.05,
          marginBottom: 32,
        }}>
          {VISION_STATEMENT.heading}
        </h2>

        <p style={{
          fontSize: 20,
          color: 'var(--ink)',
          lineHeight: 1.75,
          maxWidth: 600,
        }}>
          {VISION_STATEMENT.body}
        </p>

      </div>
    </section>
  )
}
