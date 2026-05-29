const geneDeviations = [
  { gene: 'SFTPC', score: '+4.2σ', color: '#FFFFFF' },
  { gene: 'MMP12', score: '+3.7σ', color: '#FFFFFF' },
  { gene: 'TP63',  score: '−3.1σ', color: 'rgba(148,163,184,0.8)' },
  { gene: 'FOXJ1', score: '−2.8σ', color: 'rgba(148,163,184,0.8)' },
]

export default function CasePanel() {
  return (
    <div className="case">
      <div className="head">
        <span className="id">CASE · 24-A881 · PUL</span>
        <span className="stat">REVIEW READY</span>
      </div>
      <div className="body">
        <div className="pane">
          <div className="pl">Cell composition · 847 cells profiled</div>
          <svg viewBox="0 0 240 90" width="100%" height="80">
            <g fontFamily="'Geist Mono', monospace" fontSize="8">
              <text x="4" y="20" fill="rgba(255,255,255,0.45)">AT2</text>
              <rect x="30" y="12" width="110" height="8" rx="1" fill="#FFFFFF" opacity="0.7"/>
              <text x="144" y="20" fill="#FFFFFF">+2.8σ</text>
              <text x="4" y="40" fill="rgba(255,255,255,0.45)">MΦ</text>
              <rect x="30" y="32" width="74" height="8" rx="1" fill="#FFFFFF" opacity="0.5"/>
              <text x="108" y="40" fill="#FFFFFF">+1.9σ</text>
              <text x="4" y="60" fill="rgba(255,255,255,0.45)">BAS</text>
              <rect x="30" y="52" width="124" height="8" rx="1" fill="rgba(148,163,184,0.5)"/>
              <text x="158" y="60" fill="rgba(148,163,184,0.8)">−3.1σ</text>
              <text x="4" y="80" fill="rgba(255,255,255,0.25)">END</text>
              <rect x="30" y="72" width="46" height="8" rx="1" fill="rgba(255,255,255,0.2)"/>
              <text x="80" y="80" fill="rgba(255,255,255,0.3)">−1.2σ</text>
            </g>
          </svg>
        </div>
        <div className="pane" style={{ position: 'relative' }}>
          <div className="pl">Top gene deviations · 12 outside reference</div>
          <div style={{ padding: '8px 0 4px', display: 'flex', flexDirection: 'column', gap: '5px' }}>
            {geneDeviations.map(({ gene, score, color }) => (
              <div key={gene} style={{ display: 'flex', justifyContent: 'space-between', fontFamily: "'Geist Mono', monospace", fontSize: '10px' }}>
                <span style={{ color: 'rgba(255,255,255,0.55)' }}>{gene}</span>
                <span style={{ color }}>{score}</span>
              </div>
            ))}
          </div>
          <span style={{ position: 'absolute', bottom: '10px', right: '12px', fontFamily: "'Geist Mono',monospace", fontSize: '9px', letterSpacing: '0.14em', color: 'var(--teal)' }}>
            ↳ 4 biological pathways flagged
          </span>
        </div>
      </div>
      <div className="findings">
        <div className="find">
          <span className="nm">AT2 CELLS</span>
          <span className="bar"><i style={{ width: '91%' }}></i></span>
          <span className="pct">+2.8σ</span>
        </div>
        <div className="find">
          <span className="nm">MACROPHAG.</span>
          <span className="bar"><i style={{ width: '61%' }}></i></span>
          <span className="pct">+1.9σ</span>
        </div>
        <div className="find">
          <span className="nm">BASAL CELLS</span>
          <span className="bar"><i style={{ width: '100%', background: 'var(--slate)' }}></i></span>
          <span className="pct" style={{ color: 'var(--slate)' }}>−3.1σ</span>
        </div>
      </div>
      <div className="actions">
        <button className="b primary">Confirm findings</button>
        <button className="b">Refine</button>
        <button className="b">Disagree</button>
        <button className="b" style={{ marginLeft: 'auto' }}>Open full case ↗</button>
      </div>
    </div>
  )
}
