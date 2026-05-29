import type { LayerDef } from '@/content/layers'

const layerVisuals: Record<string, React.ReactNode> = {
  L01: (
    <svg viewBox="0 0 320 80" width="100%" height="100%">
      <g stroke="#FFFFFF" strokeWidth="1" fill="none" opacity="0.7">
        <rect x="10" y="22" width="180" height="14" rx="7" />
        <rect x="10" y="44" width="120" height="14" rx="7" opacity="0.5" />
      </g>
      <circle cx="280" cy="40" r="22" fill="none" stroke="rgba(255,255,255,0.18)" />
      <circle cx="280" cy="40" r="6" fill="#FFFFFF" />
    </svg>
  ),
  L02: (
    <svg viewBox="0 0 320 80" width="100%" height="100%">
      <path d="M0,40 Q30,10 60,40 T120,40 Q150,5 180,40 T240,40 Q270,15 300,40" stroke="#FFFFFF" strokeWidth="1.2" fill="none" />
      <circle cx="180" cy="40" r="10" fill="none" stroke="#FFFFFF" />
      <circle cx="180" cy="40" r="3" fill="#FFFFFF" />
    </svg>
  ),
  L03: (
    <svg viewBox="0 0 320 80" width="100%" height="100%">
      <g stroke="rgba(255,255,255,0.18)" fill="none">
        <rect x="10" y="14" width="120" height="52" rx="6" />
        <rect x="146" y="14" width="120" height="52" rx="6" />
      </g>
      <circle cx="200" cy="40" r="8" fill="none" stroke="#FFFFFF" />
      <path d="M196,40 L199,43 L204,37" stroke="#FFFFFF" strokeWidth="1.4" fill="none" />
    </svg>
  ),
  L04: (
    <svg viewBox="0 0 320 80" width="100%" height="100%">
      <path d="M20,60 L80,20 L140,50 L200,30 L260,40 L300,25" stroke="rgba(255,255,255,0.4)" strokeWidth="1" fill="none" strokeDasharray="4,4"/>
      <circle cx="300" cy="25" r="6" fill="none" stroke="rgba(255,255,255,0.4)" />
    </svg>
  ),
}

interface Props {
  layer: LayerDef
}

export default function LayerCard({ layer }: Props) {
  const isFuture = layer.status === 'future'
  const isCore = layer.status === 'core'

  return (
    <article
      className="layer"
      style={{
        ...(isFuture ? { opacity: 0.6 } : {}),
        ...(isCore ? { background: 'rgba(255,255,255,0.025)' } : {}),
      }}
    >
      <div className="num">
        <span>{layer.label}</span>
        <span
          className="badge"
          style={isFuture ? { background: 'rgba(255,255,255,0.06)', color: 'var(--slate)' } : undefined}
        >
          {layer.badge}
        </span>
      </div>
      <div className="vis" aria-hidden="true">
        {layerVisuals[layer.id]}
      </div>
      <h3>{layer.heading}</h3>
      <p className="desc">{layer.desc}</p>
      <div className="bullets">
        {layer.bullets.map((b) => (
          <div key={b}>
            <span className="b">→</span>
            <span>{b}</span>
          </div>
        ))}
      </div>
    </article>
  )
}
