'use client';
import { useState, useEffect, useRef } from 'react';

const Logo = () => (
  <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
    <path
      d="M2 11 Q 5 11 6 8 T 9 11 T 12 14 T 15 8 T 18 11 L 20 11"
      stroke="currentColor"
      strokeWidth="1.4"
      strokeLinecap="round"
      strokeLinejoin="round"
      fill="none"
    />
  </svg>
);

const DotsIcon = () => (
  <svg width="4" height="18" viewBox="0 0 4 18" fill="currentColor">
    <circle cx="2" cy="2"  r="1.6" />
    <circle cx="2" cy="9"  r="1.6" />
    <circle cx="2" cy="16" r="1.6" />
  </svg>
);

const roles = [
  {
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
      </svg>
    ),
    title: 'Respiratory Physicians',
    desc: 'Annotate deviation findings. Board certified.',
  },
  {
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="3" />
        <path d="M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83" />
      </svg>
    ),
    title: 'Biomedical Researchers',
    desc: 'Validate reference statistics. PhD or MD/PhD.',
  },
  {
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M9 3H5a2 2 0 0 0-2 2v4m6-6h10a2 2 0 0 1 2 2v4M9 3v18m0 0h10a2 2 0 0 0 2-2v-4M9 21H5a2 2 0 0 1-2-2v-4m0 0h18" />
      </svg>
    ),
    title: 'Pathologists',
    desc: 'Correlate cellular findings with histology.',
  },
];

export default function NavBar({ active }: { active?: 'about' | 'faqs' | 'vision' | 'experts' }) {
  const [scrolled, setScrolled]   = useState(false);
  const [ddOpen,   setDdOpen]     = useState(false);
  const ddRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  useEffect(() => {
    if (!ddOpen) return;
    const onKey     = (e: KeyboardEvent) => { if (e.key === 'Escape') setDdOpen(false); };
    const onOutside = (e: MouseEvent) => {
      if (ddRef.current && !ddRef.current.contains(e.target as Node)) setDdOpen(false);
    };
    document.addEventListener('keydown', onKey);
    document.addEventListener('mousedown', onOutside);
    return () => {
      document.removeEventListener('keydown', onKey);
      document.removeEventListener('mousedown', onOutside);
    };
  }, [ddOpen]);

  const close = () => setDdOpen(false);

  return (
    <nav className={`top${scrolled ? ' scrolled' : ''}`}>
      <div className="wrap row">

        {/* Brand */}
        <a className="brand" href="/">
          <span className="mark"><Logo /></span>
          ORBREGEN
        </a>

        {/* Centre links */}
        <div className="nav-links">
          <a href="/#cycle">Platform</a>
          <a href="/#philosophy">Philosophy</a>
          <a href="/vision" style={active === 'vision' ? { color: 'var(--ink)' } : {}}>Vision</a>
          <a href="/about"  style={active === 'about'  ? { color: 'var(--ink)' } : {}}>About</a>
          <a href="/faqs"   style={active === 'faqs'   ? { color: 'var(--ink)' } : {}}>FAQs</a>
        </div>

        {/* Three-dot button — experts dropdown */}
        <div className="nav-dots-wrap" ref={ddRef}>
          <button
            className={`nav-dots-btn${ddOpen ? ' open' : ''}`}
            onClick={() => setDdOpen(d => !d)}
            aria-label="For Experts"
            aria-expanded={ddOpen}
          >
            <DotsIcon />
          </button>

          {ddOpen && (
            <div className="nav-dots-panel" role="menu">

              {/* Header */}
              <div className="nd-section">
                <div className="nd-section-label">For Medical Experts</div>
                <p className="nd-section-sub">
                  Help build the biological reference model. Shape how AI reads the human body.
                </p>
                <div className="nd-roles">
                  {roles.map(r => (
                    <a key={r.title} className="nd-role" href="/experts#who" onClick={close}>
                      <span className="nd-role-icon">{r.icon}</span>
                      <span>
                        <span className="nd-role-title">{r.title}</span>
                        <span className="nd-role-desc">{r.desc}</span>
                      </span>
                    </a>
                  ))}
                </div>
                <a className="nd-apply" href="/experts#waitlist" onClick={close}>
                  Join the waitlist <span>→</span>
                </a>
              </div>

              <div className="nd-divider" />

              {/* Mobile-only nav links */}
              <div className="nd-mobile-links">
                <a href="/#cycle"       onClick={close}>Platform</a>
                <a href="/#philosophy"  onClick={close}>Philosophy</a>
                <a href="/vision"       onClick={close} className={active === 'vision' ? 'nd-active' : ''}>Vision</a>
                <a href="/about"        onClick={close} className={active === 'about'  ? 'nd-active' : ''}>About</a>
                <a href="/faqs"         onClick={close} className={active === 'faqs'   ? 'nd-active' : ''}>FAQs</a>
              </div>

              <div className="nd-divider" />

              <div className="nd-cta-row">
                <span className="nd-cta-label">Expert onboarding opens soon</span>
                <a className="btn btn-primary nd-cta-btn" href="/experts" onClick={close}>
                  Learn more →
                </a>
              </div>

            </div>
          )}
        </div>

      </div>
    </nav>
  );
}
