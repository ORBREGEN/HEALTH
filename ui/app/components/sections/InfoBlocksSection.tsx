import { INFO_BLOCKS } from '@/content/home'

export default function InfoBlocksSection() {
  return (
    <section style={{ padding: '100px 0', borderTop: '1px solid var(--hairline)' }}>
      <div className="wrap">
        <div className="info-blocks-grid">
          {INFO_BLOCKS.map(block => (
            <div key={block.tag} style={{ borderTop: '1px solid var(--hairline)', paddingTop: 28 }}>
              <span style={{
                fontFamily: 'Geist Mono, monospace',
                fontSize: 10,
                letterSpacing: '0.16em',
                textTransform: 'uppercase',
                color: 'var(--teal)',
                display: 'block',
                marginBottom: 20,
              }}>
                {block.tag}
              </span>
              <h3 style={{
                fontFamily: 'Geist, sans-serif',
                fontWeight: 600,
                fontSize: 20,
                letterSpacing: '-0.02em',
                lineHeight: 1.2,
                marginBottom: 14,
              }}>
                {block.heading}
              </h3>
              <p style={{
                fontSize: 17,
                color: 'var(--ink)',
                lineHeight: 1.75,
                marginBottom: 24,
              }}>
                {block.body}
              </p>
              <a href={block.href} className="info-block-cta">
                {block.cta}
              </a>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
