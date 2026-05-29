import { GOAL } from '@/content/home'

export default function GoalSection() {
  return (
    <section style={{ padding: 'clamp(72px, 10vw, 140px) 0 clamp(88px, 12vw, 160px)', borderTop: '1px solid var(--hairline)' }}>
      <div className="wrap">

        <span style={{
          fontFamily: 'Geist Mono, monospace',
          fontSize: 11,
          letterSpacing: '0.16em',
          textTransform: 'uppercase',
          color: 'var(--slate)',
          display: 'block',
          marginBottom: 44,
        }}>
          {GOAL.label}
        </span>

        <p style={{
          fontFamily: '"SF Pro Display", -apple-system, BlinkMacSystemFont, system-ui, sans-serif',
          fontWeight: 100,
          fontSize: 'clamp(28px, 3.5vw, 48px)',
          lineHeight: 1.15,
          letterSpacing: '0.03em',
          color: 'var(--ink)',
          margin: '0 0 64px',
        } as React.CSSProperties}>
          {GOAL.body}
        </p>

        <a href="/vision" className="iso-cta">{GOAL.cta} →</a>

      </div>
    </section>
  )
}
