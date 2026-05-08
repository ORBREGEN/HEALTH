'use client';
import { useState } from 'react';
import NavBar from '../components/NavBar';

function WaitlistForm() {
  const [email,   setEmail]   = useState('');
  const [loading, setLoading] = useState(false);
  const [done,    setDone]    = useState(false);
  const [error,   setError]   = useState('');

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || loading) return;
    setLoading(true);
    setError('');
    try {
      const api = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';
      const res = await fetch(`${api}/api/v1/expert/waitlist`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });
      if (!res.ok) throw new Error('Request failed');
      setDone(true);
    } catch {
      setError('Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (done) {
    return (
      <div className="wl-thanks">
        <div className="wl-thanks-icon">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="20 6 9 17 4 12" />
          </svg>
        </div>
        <div>
          <div className="wl-thanks-title">You&apos;re on the list.</div>
          <div className="wl-thanks-sub">We&apos;ll reach out when expert onboarding opens. Thank you.</div>
        </div>
      </div>
    );
  }

  return (
    <form className="wl-form" onSubmit={submit}>
      <input
        className="wl-input"
        type="email"
        placeholder="your@institution.edu"
        value={email}
        onChange={e => setEmail(e.target.value)}
        required
        disabled={loading}
      />
      <button className="wl-submit" type="submit" disabled={loading}>
        {loading ? 'Sending…' : <>Join the waitlist <span>→</span></>}
      </button>
      {error && <p style={{ color: 'var(--error, #e53e3e)', fontSize: '13px', marginTop: '8px' }}>{error}</p>}
    </form>
  );
}

export default function ExpertsPage() {
  return (
    <>
      <NavBar active="experts" />

      {/* HERO */}
      <section className="ex-hero noise">
        <div className="wrap">
          <div className="ex-hero-inner">
            <div className="ex-hero-badge">
              <span className="ex-hero-badge-dot" />
              <span>Expert network — opening soon</span>
            </div>
            <h1 className="ex-hero-h1">
              Help build the reference.<br /><em>Shape how AI reads<br />the human body.</em>
            </h1>
            <p className="ex-hero-sub">
              ORBREGEN is building a biological intelligence system that starts with the lung
              and expands to every organ. The expert network is the feedback loop that makes it
              accurate. We are looking for the physicians and researchers who want to be in the
              room where this is built — not after it ships.
            </p>
            <div className="ex-hero-actions">
              <a className="btn btn-primary" href="#waitlist">Join the waitlist <span className="arrow">→</span></a>
              <a className="btn btn-ghost" href="#how">See how it works</a>
            </div>
            <div className="ex-hero-meta">
              <div className="ex-hero-stat">
                <div className="k">2.28<span>M</span></div>
                <div className="l">Human lung cells in the reference model your work refines</div>
              </div>
              <div className="ex-hero-stat">
                <div className="k">Layer 3</div>
                <div className="l">The feedback flywheel — experts are the core of the system</div>
              </div>
              <div className="ex-hero-stat">
                <div className="k">Early</div>
                <div className="l">Expert onboarding opens before the patient portal goes live</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* THE OPPORTUNITY */}
      <section className="ex-work">
        <div className="wrap">
          <span className="micro">The opportunity</span>
          <div className="ex-work-grid">
            <div className="ex-work-sticky">
              <h3>Your clinical judgment has never had this kind of leverage.</h3>
              <p>
                In clinical practice, each decision you make affects one patient. Here, each
                annotation you make trains a model that will eventually inform the care of
                thousands — people who will never have access to a specialist like you.
              </p>
              <p>
                The model describes biology. It does not name diseases. That boundary is
                deliberate. Your expertise is what crosses it — and that is exactly why
                your annotations cannot be replaced by a language model.
              </p>
            </div>
            <div className="ex-tasks">
              <div className="ex-task">
                <div className="ex-task-n">1</div>
                <div>
                  <div className="ex-task-label">Deviation review</div>
                  <div className="ex-task-title">Review AI-surfaced biological findings</div>
                  <div className="ex-task-desc">
                    The model flags deviations — cell populations outside their normal range,
                    genes with elevated Z-scores, dysregulated pathways. You review the output,
                    confirm whether the finding is clinically meaningful, and add context the
                    model cannot provide on its own.
                  </div>
                  <span className="ex-task-tag">Async · self-paced</span>
                </div>
              </div>
              <div className="ex-task">
                <div className="ex-task-n">2</div>
                <div>
                  <div className="ex-task-label">Case annotation</div>
                  <div className="ex-task-title">Annotate de-identified patient cases</div>
                  <div className="ex-task-desc">
                    De-identified cases are presented alongside deviation profiles. You annotate
                    what the deviation pattern suggests clinically, flag anything the model missed,
                    and correct errors. These annotations feed directly back into model training.
                  </div>
                  <span className="ex-task-tag">Async · self-paced</span>
                </div>
              </div>
              <div className="ex-task">
                <div className="ex-task-n">3</div>
                <div>
                  <div className="ex-task-label">Model validation</div>
                  <div className="ex-task-title">Validate reference statistics against known biology</div>
                  <div className="ex-task-desc">
                    Expert validators review whether computed distributions match what the
                    literature and clinical experience would predict — and flag inconsistencies
                    for investigation. This is the work that directly shapes the reference model.
                  </div>
                  <span className="ex-task-tag">Async · self-paced</span>
                </div>
              </div>
              <div className="ex-task">
                <div className="ex-task-n">4</div>
                <div>
                  <div className="ex-task-label">Specialist matching</div>
                  <div className="ex-task-title">Rate match quality for patient-specialist pairs</div>
                  <div className="ex-task-desc">
                    Once patient intake is live, specialists review proposed patient-to-specialist
                    matches, rate their appropriateness, and explain mismatches. This trains the
                    matching engine that determines which specialist a patient reaches.
                  </div>
                  <span className="ex-task-tag">Phase 2 — coming soon</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* WHO WE WANT */}
      <section className="ex-who" id="who">
        <div className="wrap">
          <span className="micro">Who we&apos;re looking for</span>
          <h2 className="about-section-title" style={{ marginTop: "24px" }}>
            Domain depth that<br />no language model has.
          </h2>
          <div className="ex-who-grid">
            <div className="ex-who-card">
              <div className="ex-who-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
                </svg>
              </div>
              <h3>Respiratory Physicians</h3>
              <p>
                Pulmonologists, respirologists, and thoracic specialists who can interpret
                cell-level deviations in the context of clinical presentation and disease course.
              </p>
              <div className="ex-who-reqs">
                <div className="ex-req">Board certified in pulmonology or respiratory medicine</div>
                <div className="ex-req">Active or recent clinical practice</div>
                <div className="ex-req">Interest in how AI reads biological data</div>
              </div>
            </div>
            <div className="ex-who-card">
              <div className="ex-who-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="3" />
                  <path d="M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83" />
                </svg>
              </div>
              <h3>Biomedical Researchers</h3>
              <p>
                Academic researchers in lung biology, respiratory immunology, or single-cell
                genomics who can assess whether computed reference statistics reflect known biology.
              </p>
              <div className="ex-who-reqs">
                <div className="ex-req">PhD or MD/PhD in a relevant biological field</div>
                <div className="ex-req">Active or recent research in pulmonary or cell biology</div>
                <div className="ex-req">Familiarity with transcriptomic data a plus</div>
              </div>
            </div>
            <div className="ex-who-card">
              <div className="ex-who-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M9 3H5a2 2 0 0 0-2 2v4m6-6h10a2 2 0 0 1 2 2v4M9 3v18m0 0h10a2 2 0 0 0 2-2v-4M9 21H5a2 2 0 0 1-2-2v-4m0 0h18" />
                </svg>
              </div>
              <h3>Pathologists</h3>
              <p>
                Pulmonary pathologists who can correlate cellular-level deviation profiles
                with tissue-level pathological findings — grounding the model&apos;s spatial
                inference in histological reality.
              </p>
              <div className="ex-who-reqs">
                <div className="ex-req">Board certified in anatomical or clinical pathology</div>
                <div className="ex-req">Interest in pulmonary or thoracic pathology</div>
                <div className="ex-req">Curiosity about cellular-level AI findings</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="ex-how" id="how">
        <div className="wrap">
          <span className="micro">How it works</span>
          <h2 className="about-section-title" style={{ marginTop: "24px" }}>
            Designed to fit around<br />a clinical schedule.
          </h2>
          <div className="ex-how-steps">
            <div className="ex-step">
              <div className="ex-step-n">Step 01</div>
              <h3>Join the waitlist</h3>
              <p>
                Leave your email and specialty. We will reach out when expert onboarding opens —
                before the patient portal goes live, so early network members shape the workflow
                before it hardens.
              </p>
            </div>
            <div className="ex-step">
              <div className="ex-step-n">Step 02</div>
              <h3>Credential and onboard</h3>
              <p>
                We verify background and specialty, then walk you through how the model works,
                what a deviation profile looks like, and what good annotation looks like.
                One async session. No long training programmes.
              </p>
            </div>
            <div className="ex-step">
              <div className="ex-step-n">Step 03</div>
              <h3>Review cases on your time</h3>
              <p>
                Tasks are available on demand through the expert platform. You pick up cases
                when you have time — between rounds, in the evening, whenever. No minimum
                commitment, no fixed schedule.
              </p>
            </div>
            <div className="ex-step">
              <div className="ex-step-n">Step 04</div>
              <h3>Watch the model improve</h3>
              <p>
                Your annotations are incorporated into the next training cycle. You can track
                how your contributions have shaped model behaviour — and see the cases where
                your correction propagated forward.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* IMPACT */}
      <section className="ex-impact noise">
        <div className="wrap">
          <span className="micro">Why it matters</span>
          <p className="ex-impact-quote">
            &ldquo;The model describes biology.<br /><em>You name what it means.</em><br />That boundary is the whole point.&rdquo;
          </p>
          <div className="ex-impact-body">
            <div>
              <div className="ex-impact-item-n">Direct model impact</div>
              <h3>Your annotations go straight into training</h3>
              <p>
                Every case you annotate is fed back into the model within the next training cycle.
                When you correct a deviation assessment, the correction propagates across every
                future case where that pattern appears. You are not filling a spreadsheet — you
                are reshaping how the model understands biology.
              </p>
            </div>
            <div>
              <div className="ex-impact-item-n">Provenance &amp; credit</div>
              <h3>Your contribution is tracked and attributed</h3>
              <p>
                Expert annotations carry provenance metadata — specialty, agreement rate with
                other annotators, influence on model behaviour. Expert advisors who shape model
                behaviour at a structural level are credited by name in model documentation
                and any research publications.
              </p>
            </div>
            <div>
              <div className="ex-impact-item-n">Scale of reach</div>
              <h3>One annotation, thousands of future patients</h3>
              <p>
                A model that serves patient matching at scale means that a single well-placed
                correction ripples across every future case where that pattern appears. One
                expert hour improving accuracy for patients you will never meet, in places
                you will never go.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* WAITLIST */}
      <section className="ex-cta" id="waitlist">
        <div className="wrap">
          <h2>
            Be in the room<br /><em>where it&apos;s built.</em>
          </h2>
          <p>
            Expert onboarding opens before the patient portal goes live. Waitlist members
            are first in — and shape the workflow before it is set in stone.
          </p>
          <WaitlistForm />
          <div className="wl-note">
            No spam. No obligation. We will email you once when onboarding opens.
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
                    <path d="M2 11 Q 5 11 6 8 T 9 11 T 12 14 T 15 8 T 18 11 L 20 11"
                      stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" fill="none" />
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
                <li><a href="/vision">Vision &amp; Mission</a></li>
                <li><a href="/experts">For Experts</a></li>
                <li><a href="#">Careers</a></li>
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
