import { BLOCKS } from '@/content/home'

export default function BlocksSection() {
  return (
    <section style={{ borderTop: '1px solid var(--hairline)', padding: '100px 0' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)' }}>
        {BLOCKS.map((block, i) => (
          <div key={block.label} style={{
            border: '1px solid var(--hairline)',
            padding: '52px 40px 56px',
            marginLeft: i > 0 ? -1 : 0,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            minHeight: 300,
          }}>
            <div>
              <div className="iso-label" style={{ marginBottom: 32 }}>{block.label}</div>
              <h3 style={{
                fontSize: 'clamp(20px, 2vw, 26px)',
                fontWeight: 100,
                lineHeight: 1.3,
                letterSpacing: '0.02em',
                color: 'var(--ink)',
              }}>
                {block.heading}
              </h3>
            </div>
            <a href={block.href} className="iso-cta iso-cta--muted" style={{ marginTop: 48 }}>
              {block.link} →
            </a>
          </div>
        ))}
      </div>
    </section>
  )
}
