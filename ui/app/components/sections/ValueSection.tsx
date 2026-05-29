import { VALUE } from '@/content/home'

export default function ValueSection() {
  return (
    <section className="philosophy">
      <div className="wrap">
        <div className="philosophy-intro" style={{ textAlign: 'left', margin: 0, maxWidth: 820 }}>
          <span className="micro">{VALUE.eyebrow}</span>
          <p className="philosophy-statement" style={{ marginTop: 24 }}>{VALUE.heading}</p>
          <p className="philosophy-lead" style={{ marginTop: 20, maxWidth: 640 }}>{VALUE.intro}</p>
        </div>
        <div className="philosophy-pillars">
          {VALUE.points.map((point, i) => (
            <div className="pillar" key={i}>
              <div className="pn">{String(i + 1).padStart(2, '0')}</div>
              <h3>{point.heading}</h3>
              <p>{point.body}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
