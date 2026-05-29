export default function CellImageSection() {
  return (
    <section style={{ overflow: 'hidden', position: 'relative' }}>
      <div style={{ position: 'relative', height: '75vh', minHeight: 500 }}>
        <img
          src="/images/cell-single.jpg"
          alt=""
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            objectPosition: 'center',
            display: 'block',
          }}
        />
        <div style={{
          position: 'absolute',
          inset: 0,
          background: 'linear-gradient(to bottom, var(--navy) 0%, transparent 18%, transparent 78%, var(--navy) 100%)',
          pointerEvents: 'none',
        }} />
        <div style={{
          position: 'absolute',
          bottom: 36,
          right: 48,
          fontFamily: 'Geist Mono, monospace',
          fontSize: 10,
          letterSpacing: '0.14em',
          textTransform: 'uppercase',
          color: 'rgba(248,250,252,0.30)',
        }}>
          Human lung cells · HLCA reference model
        </div>
      </div>
    </section>
  )
}
