import { LATEST } from '@/content/home'

export default function LatestSection() {
  return (
    <section style={{ borderTop: '1px solid var(--hairline)', paddingBottom: '100px' }}>

      <div style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        padding: '48px 0 40px',
      }}>
        <span className="iso-label">{LATEST.label}</span>
        <a href="#" className="iso-cta iso-cta--muted">View all →</a>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)' }}>
        {LATEST.cards.map((card, i) => (
          <div key={card.heading} style={{
            border: '1px solid var(--hairline)',
            padding: '40px 36px 52px',
            marginLeft: i > 0 ? -1 : 0,
          }}>
            <div className="iso-label" style={{ color: 'var(--teal)', marginBottom: 28 }}>
              {card.tag}
            </div>
            <h3 style={{
              fontSize: 'clamp(17px, 1.8vw, 22px)',
              fontWeight: 100,
              lineHeight: 1.35,
              letterSpacing: '0.02em',
              color: 'var(--ink)',
            }}>
              {card.heading}
            </h3>
          </div>
        ))}
      </div>

    </section>
  )
}
