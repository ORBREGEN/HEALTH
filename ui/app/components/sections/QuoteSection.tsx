import { QUOTE } from '@/content/home'

export default function QuoteSection() {
  return (
    <section style={{ padding: '140px 0', borderTop: '1px solid var(--hairline)' }}>
      <div className="wrap" style={{ maxWidth: 860 }}>

        <p style={{
          fontFamily: 'Geist, sans-serif',
          fontWeight: 400,
          fontSize: 'clamp(22px, 3vw, 36px)',
          lineHeight: 1.45,
          letterSpacing: '-0.02em',
          marginBottom: 40,
        }}>
          &ldquo;{QUOTE.text}&rdquo;
        </p>

        <span style={{
          fontFamily: 'Geist Mono, monospace',
          fontSize: 11,
          letterSpacing: '0.16em',
          textTransform: 'uppercase',
          color: 'var(--slate)',
        }}>
          {QUOTE.attr}
        </span>

      </div>
    </section>
  )
}
