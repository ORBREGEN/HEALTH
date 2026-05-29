import { LAYERS } from '@/content/layers'

export default function LayersSection() {
  return (
    <section style={{ padding: '120px 0', borderTop: '1px solid var(--hairline)' }}>
      <div className="wrap">

        <div style={{ marginBottom: 80 }}>
          <span style={{
            fontFamily: 'Geist Mono, monospace',
            fontSize: 11,
            letterSpacing: '0.16em',
            textTransform: 'uppercase',
            color: 'var(--teal)',
            display: 'block',
            marginBottom: 20,
          }}>
            What we are building
          </span>
          <h2 style={{
            fontFamily: 'Geist, sans-serif',
            fontWeight: 600,
            fontSize: 'clamp(28px, 4vw, 48px)',
            letterSpacing: '-0.03em',
            lineHeight: 1.1,
            maxWidth: 560,
          }}>
            Four layers. One platform.
          </h2>
        </div>

        <div className="layers-home">
          {LAYERS.map((layer) => (
            <div key={layer.id} className="layer-home-col">
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: 40,
              }}>
                <span style={{
                  fontFamily: 'Geist Mono, monospace',
                  fontSize: 10,
                  letterSpacing: '0.16em',
                  textTransform: 'uppercase',
                  color: 'var(--slate)',
                }}>
                  {layer.label}
                </span>
                {layer.status === 'future' && (
                  <span style={{
                    fontFamily: 'Geist Mono, monospace',
                    fontSize: 9,
                    letterSpacing: '0.12em',
                    textTransform: 'uppercase',
                    color: 'var(--teal)',
                    border: '1px solid rgba(255,255,255,0.25)',
                    padding: '3px 8px',
                    borderRadius: 999,
                  }}>
                    {layer.badge}
                  </span>
                )}
              </div>

              <h3 style={{
                fontFamily: 'Geist, sans-serif',
                fontWeight: 600,
                fontSize: 18,
                letterSpacing: '-0.02em',
                lineHeight: 1.25,
                marginBottom: 16,
              }}>
                {layer.heading}
              </h3>

              <p style={{
                fontSize: 17,
                color: 'var(--ink)',
                lineHeight: 1.75,
                marginBottom: 28,
              }}>
                {layer.desc}
              </p>

              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 8 }}>
                {layer.bullets.map(b => (
                  <li key={b} style={{
                    fontSize: 15,
                    color: 'var(--ink)',
                    lineHeight: 1.5,
                    paddingLeft: 16,
                    position: 'relative',
                  }}>
                    <span style={{
                      position: 'absolute',
                      left: 0,
                      color: 'var(--teal)',
                      fontFamily: 'Geist Mono, monospace',
                      fontSize: 10,
                      top: 2,
                    }}>·</span>
                    {b}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

      </div>
    </section>
  )
}
