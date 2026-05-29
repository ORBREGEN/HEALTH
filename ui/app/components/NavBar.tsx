const Logo = () => (
  <svg width="26" height="26" viewBox="0 0 26 26" fill="none">
    <circle cx="13" cy="13" r="11" stroke="currentColor" strokeWidth="1.6" fill="none"/>
    <path d="M 4 11 C 7 5 11 6 13 9.5 C 15 13 19 12 22 8"
          stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" fill="none"/>
    <path d="M 4 18 C 7 12 11 13 13 16.5 C 15 20 19 19 22 15"
          stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" fill="none"/>
  </svg>
);

export default function NavBar({ active }: { active?: 'home' | 'patients' | 'about' | 'faqs' | 'analyse' | 'experts' | 'vision' | 'contribute' }) {
  return (
    <nav className="top scrolled">
      <div className="wrap row">

        <a className="brand" href="/">
          <span className="mark"><Logo /></span>
          Senebiclabs
        </a>

        <div className="nav-links">
          <a href="/patients"   style={active === 'patients'   ? { color: 'var(--ink)' } : {}}>Patients</a>
          <a href="/experts"    style={active === 'experts'    ? { color: 'var(--ink)' } : {}}>Specialists</a>
          <a href="/contribute" style={active === 'contribute' ? { color: 'var(--ink)' } : {}}>Contribute</a>
          <a href="/analyse"    style={active === 'analyse'    ? { color: 'var(--ink)' } : {}}>Research</a>
          <a href="/about"      style={active === 'about'      ? { color: 'var(--ink)' } : {}}>About</a>
        </div>

        <a href="/experts" className="nav-join-cta">Join as specialist →</a>

      </div>
    </nav>
  );
}
