import { NAME_SECTION } from '@/content/home'

export default function NameSection() {
  return (
    <section style={{ padding: '120px 0', borderTop: '1px solid var(--hairline)' }}>
      <div className="wrap" style={{ maxWidth: 760 }}>

        <h2 style={{
          fontFamily: 'Geist, sans-serif',
          fontWeight: 600,
          fontSize: 'clamp(28px, 3.5vw, 44px)',
          letterSpacing: '-0.03em',
          lineHeight: 1.1,
          marginBottom: 36,
        }}>
          {NAME_SECTION.heading}
        </h2>

        <p style={{
          fontSize: 20,
          lineHeight: 1.75,
          marginBottom: 20,
        }}>
          {NAME_SECTION.body1}
        </p>

        <p style={{
          fontSize: 20,
          lineHeight: 1.75,
          color: 'var(--ink)',
        }}>
          {NAME_SECTION.body2}
        </p>

      </div>
    </section>
  )
}
