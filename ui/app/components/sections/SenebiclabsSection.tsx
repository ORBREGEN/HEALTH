import { SENEBICLABS_SECTION } from '@/content/home'

export default function SenebiclabsSection() {
  return (
    <section style={{ padding: '120px 0', borderTop: '1px solid var(--hairline)' }}>
      <div style={{
        display: 'grid',
        gridTemplateColumns: '240px 1fr',
        gap: '0 80px',
        alignItems: 'start',
      }}>
        <div className="iso-label" style={{ paddingTop: 6 }}>
          {SENEBICLABS_SECTION.label}
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 28 }}>
          {[SENEBICLABS_SECTION.p1, SENEBICLABS_SECTION.p2, SENEBICLABS_SECTION.p3].map((p, i) => (
            <p key={i} style={{
              fontSize: i === 0 ? 'clamp(20px, 2vw, 26px)' : 'clamp(17px, 1.6vw, 20px)',
              fontWeight: i === 0 ? 300 : 400,
              lineHeight: 1.75,
              letterSpacing: '0.01em',
              color: 'var(--ink)',
            }}>
              {p}
            </p>
          ))}
        </div>
        <div style={{ marginTop: 48 }}>
          <a href="/vision" className="iso-cta">Explore the science →</a>
        </div>
      </div>
    </section>
  )
}
