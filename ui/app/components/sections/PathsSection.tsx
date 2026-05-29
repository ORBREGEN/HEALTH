import { AUDIENCES, type AudienceCard } from '@/content/home'

function Column({ card }: { card: AudienceCard }) {
  return (
    <div style={{ borderTop: '1px solid var(--hairline)', paddingTop: 28, display: 'flex', flexDirection: 'column' }}>
      <span style={{
        fontFamily: 'Geist Mono, monospace',
        fontSize: 10,
        letterSpacing: '0.16em',
        textTransform: 'uppercase',
        color: 'var(--teal)',
        marginBottom: 18,
      }}>
        {card.tag}
      </span>
      <h3 style={{
        fontFamily: 'Geist, sans-serif',
        fontSize: 18,
        fontWeight: 600,
        letterSpacing: '-0.02em',
        lineHeight: 1.2,
        marginBottom: 14,
      }}>
        {card.heading}
      </h3>
      <p style={{
        fontSize: 17,
        color: 'var(--ink)',
        lineHeight: 1.7,
        flex: 1,
      }}>
        {card.body}
      </p>
      <a href={card.href} className="paths-cta">
        {card.cta}
      </a>
    </div>
  )
}

export default function PathsSection() {
  return (
    <section style={{ padding: '100px 0 140px' }}>
      <div className="wrap">
        <div className="paths-grid" style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: '0 56px',
        }}>
          {AUDIENCES.map(card => (
            <Column key={card.tag} card={card} />
          ))}
        </div>
      </div>
    </section>
  )
}
