import NavBar from '../components/NavBar';

export default function AboutPage() {
  return (
    <>
      <NavBar active="about" />

      {/* HERO */}
      <section className="about-hero noise">
        <div className="wrap">
          <span className="micro">About us</span>
          <h1 className="about-headline">
            Built to understand<br /><em>healthy human biology.</em>
          </h1>
          <p className="about-sub">
            ORBREGEN is a biological intelligence platform built on one foundational
            insight: if a system deeply understands what a healthy human body looks
            like at the cellular level, it can detect anything that deviates from
            that — and eventually guide the correction of it. We are starting with
            the respiratory system.
          </p>
        </div>
      </section>

      {/* ORIGIN */}
      <section className="about-origin">
        <div className="wrap">
          <div className="about-origin-grid">
            <div>
              <span className="micro">The origin</span>
              <h2 className="about-section-title" style={{ marginTop: "24px" }}>
                A question no one<br />had properly answered.
              </h2>
            </div>
            <div className="about-origin-body">
              <p>
                We began with a question that sounds simple and isn&apos;t: what does
                a healthy human body actually look like — not at the organ level, not
                at the tissue level, but at the level of individual cells, across
                every donor, every tissue, every condition?
              </p>
              <p>
                The respiratory system is where we started — the data existed, the
                clinical need was clear, and the Human Lung Cell Atlas gave us
                2.28 million annotated human lung cells to build from. We built our
                reference from the normal cells in that atlas, computing statistics
                from the data, not writing them by hand.
              </p>
              <p>
                From that reference, everything else follows. A system that knows
                what healthy looks like at cellular resolution can describe any
                deviation from it — without being told what to look for. The
                same method applies to every organ system.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* FOUNDING INSIGHT */}
      <section className="about-insight noise">
        <div className="wrap">
          <p className="about-insight-quote">
            &ldquo;Most medical AI learns from labels.<br />We learned from cells.&rdquo;
          </p>
        </div>
      </section>

      {/* NUMBERS — all from CLAUDE.md */}
      <section className="about-numbers">
        <div className="wrap">
          <div className="about-numbers-grid">
            <div className="about-stat">
              <div className="about-stat-k">2.28<span>M</span></div>
              <div className="about-stat-l">Human lung cells in the reference model</div>
            </div>
            <div className="about-stat">
              <div className="about-stat-k">16</div>
              <div className="about-stat-l">Disease states present in the atlas</div>
            </div>
            <div className="about-stat">
              <div className="about-stat-k">55,329</div>
              <div className="about-stat-l">Genes profiled across the full dataset</div>
            </div>
            <div className="about-stat">
              <div className="about-stat-k">4</div>
              <div className="about-stat-l">Interconnected layers of intelligence</div>
            </div>
          </div>
        </div>
      </section>

      {/* APPROACH */}
      <section className="about-approach">
        <div className="wrap">
          <div className="about-approach-head">
            <span className="micro">How we work</span>
            <h2 className="about-section-title" style={{ marginTop: "24px" }}>
              Three commitments we<br />hold without exception.
            </h2>
          </div>
          <div className="about-approach-grid">
            <div className="about-commit">
              <div className="about-commit-n">I</div>
              <h3>Compute what others curate</h3>
              <p>
                Nothing biological is hardcoded. No curated gene lists, no
                manually written disease signatures. Every reference statistic
                comes from the HLCA cells. If we cannot derive it from the
                data, we do not make it.
              </p>
            </div>
            <div className="about-commit">
              <div className="about-commit-n">II</div>
              <h3>Surface findings, defer to experts</h3>
              <p>
                The model describes biology. Experts name diseases. We are
                rigorous about this boundary — the API returns deviations,
                Z-scores, and pathway states. It does not return disease
                names. Clinical judgment belongs to a clinician.
              </p>
            </div>
            <div className="about-commit">
              <div className="about-commit-n">III</div>
              <h3>Build the flywheel before the product</h3>
              <p>
                Patient matching is only as good as the underlying model.
                The model is only as good as the expert feedback that refines
                it. We build in sequence — Layer 2 before Layer 1, reference
                before matching, understanding before treatment.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* TEAM — placeholder until real info is provided */}
      <section className="about-team">
        <div className="wrap">
          <span className="micro">The team</span>
          <h2 className="about-section-title" style={{ marginTop: "24px", marginBottom: "32px" }}>
            Small by design.<br /><em>Deep by necessity.</em>
          </h2>
          <p style={{ fontSize: "16px", lineHeight: "1.65", color: "var(--slate)", maxWidth: "560px" }}>
            Team details coming soon.
          </p>
        </div>
      </section>

      {/* CONTACT */}
      <section className="about-join noise">
        <div className="wrap">
          <div className="about-join-inner">
            <div>
              <span className="micro">Get in touch</span>
              <h2 className="about-section-title" style={{ marginTop: "24px" }}>
                Work with us.
              </h2>
              <p style={{ marginTop: "18px", fontSize: "16px", lineHeight: "1.65", color: "var(--slate)", maxWidth: "440px" }}>
                We are working with research institutions, pulmonology groups,
                and hospital systems. If you want to be part of the clinical
                preview, reach out directly.
              </p>
            </div>
            <div className="open-roles">
              <a className="role" href="/#cta">
                <div>
                  <div className="role-title">Clinical partners</div>
                  <div className="role-meta">Pulmonology groups · Hospital systems · Research institutions</div>
                </div>
                <span className="role-arrow">→</span>
              </a>
              <a className="role" href="/#cta">
                <div>
                  <div className="role-title">Research API access</div>
                  <div className="role-meta">Academic labs · Non-commercial use · Data-use agreement</div>
                </div>
                <span className="role-arrow">→</span>
              </a>
              <a className="role" href="/#cta">
                <div>
                  <div className="role-title">Expert network</div>
                  <div className="role-meta">Certified respiratory physicians · Annotators · Advisors</div>
                </div>
                <span className="role-arrow">→</span>
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer>
        <div className="wrap">
          <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr 1fr 1fr", gap: "64px" }}>
            <div>
              <a className="brand" href="/">
                <span className="mark">
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
                </span>
                ORBREGEN
              </a>
              <p style={{ marginTop: "18px", maxWidth: "300px", lineHeight: "1.6", color: "var(--slate)", fontSize: "13.5px" }}>
                Biological intelligence connecting patients, clinicians,
                and the research community — starting with respiratory.
              </p>
            </div>
            <div>
              <h5>Platform</h5>
              <ul>
                <li><a href="/#patient">For Patients</a></li>
                <li><a href="/#clinic">For Clinicians</a></li>
                <li><a href="/#engine">AI Engine</a></li>
                <li><a href="#">Research API</a></li>
              </ul>
            </div>
            <div>
              <h5>Company</h5>
              <ul>
                <li><a href="/about">About</a></li>
                <li><a href="#">Research</a></li>
                <li><a href="#">Careers</a></li>
                <li><a href="#">Press</a></li>
              </ul>
            </div>
            <div>
              <h5>Trust</h5>
              <ul>
                <li><a href="#">Privacy</a></li>
                <li><a href="#">Data ethics</a></li>
                <li><a href="#">Security</a></li>
                <li><a href="#">Regulatory</a></li>
              </ul>
            </div>
          </div>
          <div className="legal">
            <span>© 2026 ORBREGEN Inc. · All rights reserved</span>
            <span>Built for the air we share.</span>
          </div>
        </div>
      </footer>
    </>
  );
}
