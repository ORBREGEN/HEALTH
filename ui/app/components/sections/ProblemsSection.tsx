import { PROBLEMS } from '@/content/home'

export default function ProblemsSection() {
  return (
    <section style={{ padding: '120px 0', borderTop: '1px solid var(--hairline)' }}>
      <div className="wrap">
        <div className="problems-grid">
          {PROBLEMS.map((item, i) => (
            <div key={i} style={{ borderTop: '1px solid var(--hairline)', paddingTop: 32 }}>
              <h3 style={{
                fontFamily: 'Geist, sans-serif',
                fontWeight: 600,
                fontSize: 20,
                letterSpacing: '-0.02em',
                lineHeight: 1.25,
                marginBottom: 18,
              }}>
                {item.heading}
              </h3>
              <p style={{
                fontSize: 17,
                color: 'var(--ink)',
                lineHeight: 1.8,
              }}>
                {item.body}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
