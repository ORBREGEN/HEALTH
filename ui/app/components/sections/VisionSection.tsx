import { VISION_BLOCK } from '@/content/home'

export default function VisionSection() {
  return (
    <section style={{ padding: '140px 0 160px', borderTop: '1px solid var(--hairline)' }}>
      <div className="wrap" style={{ textAlign: 'center' }}>

        <span style={{
          fontFamily: 'Geist Mono, monospace',
          fontSize: 11,
          letterSpacing: '0.16em',
          textTransform: 'uppercase',
          color: 'var(--teal)',
          display: 'block',
          marginBottom: 32,
        }}>
          {VISION_BLOCK.label}
        </span>

        <h2 style={{
          fontFamily: 'Geist, sans-serif',
          fontWeight: 600,
          fontSize: 'clamp(36px, 5.5vw, 72px)',
          letterSpacing: '-0.04em',
          lineHeight: 1.05,
          whiteSpace: 'pre-line',
          marginBottom: 36,
          textWrap: 'balance',
        } as React.CSSProperties}>
          {VISION_BLOCK.statement}
        </h2>

        <p style={{
          fontSize: 18,
          color: 'var(--ink)',
          lineHeight: 1.75,
          maxWidth: 560,
          margin: '0 auto',
          textWrap: 'pretty',
        } as React.CSSProperties}>
          {VISION_BLOCK.body}
        </p>

      </div>
    </section>
  )
}
