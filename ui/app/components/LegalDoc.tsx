import NavBar from './NavBar'
import FooterSection from './sections/FooterSection'

export function Section({ heading, children }: { heading: string; children: React.ReactNode }) {
  return (
    <section style={{ marginBottom: 44 }}>
      <h2 style={{
        fontFamily: 'Geist, sans-serif',
        fontSize: 'clamp(18px, 2vw, 22px)',
        fontWeight: 500,
        letterSpacing: '-0.01em',
        color: 'var(--ink)',
        marginBottom: 16,
      }}>
        {heading}
      </h2>
      <div style={{
        fontSize: 'clamp(15px, 1.4vw, 16px)',
        lineHeight: 1.8,
        color: 'var(--slate)',
        fontWeight: 300,
      }}>
        {children}
      </div>
    </section>
  )
}

export default function LegalDoc({
  title, updated, intro, children,
}: {
  title: string
  updated: string
  intro: string
  children: React.ReactNode
}) {
  return (
    <>
      <NavBar />
      <section style={{ padding: 'clamp(120px, 15vw, 180px) 0 clamp(40px, 5vw, 64px)' }}>
        <div className="wrap" style={{ maxWidth: 760 }}>
          <span style={{
            fontFamily: 'Geist Mono, monospace',
            fontSize: 13,
            letterSpacing: '0.14em',
            textTransform: 'uppercase' as const,
            color: 'var(--slate)',
            display: 'block',
            marginBottom: 20,
          }}>
            Legal
          </span>
          <h1 style={{
            fontFamily: '"SF Pro Display", -apple-system, BlinkMacSystemFont, system-ui, sans-serif',
            fontWeight: 100,
            fontSize: 'clamp(34px, 5vw, 60px)',
            lineHeight: 1.05,
            letterSpacing: '0.02em',
            marginBottom: 20,
          }}>
            {title}
          </h1>
          <p style={{ fontFamily: 'Geist Mono, monospace', fontSize: 13, color: 'var(--slate-2)', marginBottom: 36 }}>
            Last updated: {updated}
          </p>
          <p style={{ fontSize: 'clamp(16px, 1.5vw, 18px)', lineHeight: 1.8, color: 'var(--ink)', fontWeight: 300 }}>
            {intro}
          </p>
        </div>
      </section>

      <section style={{ padding: '0 0 clamp(64px, 8vw, 100px)', borderTop: '1px solid var(--hairline)' }}>
        <div className="wrap" style={{ maxWidth: 760, paddingTop: 'clamp(40px, 5vw, 64px)' }}>
          {children}
        </div>
      </section>

      <FooterSection />
    </>
  )
}
