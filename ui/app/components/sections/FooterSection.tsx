import { FOOTER } from '@/content/home'

export default function FooterSection() {
  return (
    <footer>
      <div className="wrap">
        <div className="grid">
          <div>
            <a className="brand" href="/">
              <span className="mark">
                <svg width="26" height="26" viewBox="0 0 26 26" fill="none">
                  <circle cx="13" cy="13" r="11" stroke="currentColor" strokeWidth="1.6" fill="none"/>
                  <path d="M 4 11 C 7 5 11 6 13 9.5 C 15 13 19 12 22 8"
                        stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" fill="none"/>
                  <path d="M 4 18 C 7 12 11 13 13 16.5 C 15 20 19 19 22 15"
                        stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" fill="none"/>
                </svg>
              </span>
              Senebiclabs
            </a>
            <p style={{ marginTop: '18px', maxWidth: '300px', lineHeight: '1.6', color: 'var(--slate)', fontSize: '13.5px' }}>
              {FOOTER.tagline}
            </p>
          </div>
          <div>
            <h5>Platform</h5>
            <ul>
              {FOOTER.nav.platform.map((item) => (
                <li key={item.label}><a href={item.href}>{item.label}</a></li>
              ))}
            </ul>
          </div>
          <div>
            <h5>Company</h5>
            <ul>
              {FOOTER.nav.company.map((item) => (
                <li key={item.label}><a href={item.href}>{item.label}</a></li>
              ))}
            </ul>
          </div>
          <div>
            <h5>Trust</h5>
            <ul>
              {FOOTER.nav.trust.map((item) => (
                <li key={item.label}><a href={item.href}>{item.label}</a></li>
              ))}
            </ul>
          </div>
        </div>
        <div className="legal">
          <span>{FOOTER.legal}</span>
          <span style={{ fontFamily: 'var(--font-mono, monospace)', fontSize: 11, letterSpacing: '0.08em' }}>
            For research use only · Not a medical device · Does not constitute medical advice
          </span>
          <span>{FOOTER.legal2}</span>
        </div>
      </div>
    </footer>
  )
}
