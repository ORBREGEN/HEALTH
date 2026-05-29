import { BLOCKS } from '@/content/home'

export default function BlocksSection() {
  return (
    <section style={{ borderTop: '1px solid var(--hairline)', padding: 'clamp(56px, 8vw, 100px) 0' }}>
      <div className="wrap">
        <div className="blocks-3col">
          {BLOCKS.map((block, i) => (
            <div key={block.label} style={{
              border: '1px solid var(--hairline)',
              padding: 'clamp(28px, 4vw, 52px) clamp(20px, 3vw, 40px) clamp(32px, 4.5vw, 56px)',
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
      </div>
    </section>
  )
}
