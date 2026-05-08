import NavBar from './components/NavBar';

export default function HomePage() {
  return (
    <>
      <NavBar />

      {/* HERO */}
      <section className="hero noise">
        <div className="sphere-container">
          <div className="sphere-glow" />
          <div className="sphere-body">
            <svg className="sphere-particles" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><circle cx="53.64" cy="50" r="0.35" fill="white" opacity="0.08"/><circle cx="45.36" cy="54.25" r="0.51" fill="white" opacity="0.15"/><circle cx="50.71" cy="41.9" r="0.67" fill="white" opacity="0.22"/><circle cx="55.85" cy="57.64" r="0.83" fill="white" opacity="0.29"/><circle cx="39.26" cy="48.1" r="0.99" fill="white" opacity="0.36"/><circle cx="60.18" cy="43.53" r="0.35" fill="white" opacity="0.43"/><circle cx="46.6" cy="62.66" r="0.51" fill="white" opacity="0.5"/><circle cx="43.51" cy="37.5" r="0.67" fill="white" opacity="0.57"/><circle cx="64.08" cy="55.14" r="0.83" fill="white" opacity="0.64"/><circle cx="35.35" cy="56.05" r="0.99" fill="white" opacity="0.08"/><circle cx="57.06" cy="34.91" r="0.35" fill="white" opacity="0.15"/><circle cx="55.22" cy="66.64" r="0.51" fill="white" opacity="0.22"/><circle cx="34.27" cy="40.88" r="0.67" fill="white" opacity="0.29"/><circle cx="68.46" cy="45.94" r="0.83" fill="white" opacity="0.36"/><circle cx="38.74" cy="66.02" r="0.99" fill="white" opacity="0.43"/><circle cx="47.4" cy="29.92" r="0.35" fill="white" opacity="0.5"/><circle cx="65.97" cy="63.46" r="0.51" fill="white" opacity="0.57"/><circle cx="28.5" cy="50.89" r="0.67" fill="white" opacity="0.64"/><circle cx="65.68" cy="34.4" r="0.83" fill="white" opacity="0.08"/><circle cx="48.95" cy="72.69" r="0.99" fill="white" opacity="0.15"/><circle cx="35.08" cy="32.12" r="0.35" fill="white" opacity="0.22"/><circle cx="73.63" cy="53.18" r="0.51" fill="white" opacity="0.29"/><circle cx="29.98" cy="63.93" r="0.67" fill="white" opacity="0.36"/><circle cx="55.47" cy="25.68" r="0.83" fill="white" opacity="0.43"/><circle cx="62.66" cy="72.09" r="0.99" fill="white" opacity="0.5"/><circle cx="25.26" cy="42.11" r="0.35" fill="white" opacity="0.57"/><circle cx="74.03" cy="38.9" r="0.51" fill="white" opacity="0.64"/><circle cx="39.59" cy="74.88" r="0.67" fill="white" opacity="0.08"/><circle cx="40.71" cy="24.16" r="0.83" fill="white" opacity="0.15"/><circle cx="74.73" cy="63" r="0.99" fill="white" opacity="0.22"/><circle cx="22.54" cy="57.24" r="0.35" fill="white" opacity="0.29"/><circle cx="65.61" cy="25.72" r="0.51" fill="white" opacity="0.36"/><circle cx="54.97" cy="78.9" r="0.67" fill="white" opacity="0.43"/><circle cx="26.47" cy="31.77" r="0.83" fill="white" opacity="0.5"/><circle cx="80.1" cy="47.51" r="0.99" fill="white" opacity="0.57"/><circle cx="29.19" cy="72.49" r="0.35" fill="white" opacity="0.64"/><circle cx="50.15" cy="18.93" r="0.51" fill="white" opacity="0.08"/><circle cx="71.16" cy="73.33" r="0.67" fill="white" opacity="0.15"/><circle cx="18.22" cy="47.06" r="0.83" fill="white" opacity="0.22"/><circle cx="75.75" cy="30.46" r="0.99" fill="white" opacity="0.29"/><circle cx="44.14" cy="82.2" r="0.35" fill="white" opacity="0.36"/><circle cx="32.35" cy="21.96" r="0.51" fill="white" opacity="0.43"/><circle cx="82.34" cy="58.86" r="0.67" fill="white" opacity="0.5"/><circle cx="19.82" cy="65.49" r="0.83" fill="white" opacity="0.57"/><circle cx="61.93" cy="17.83" r="0.99" fill="white" opacity="0.64"/><circle cx="63.08" cy="82.13" r="0.35" fill="white" opacity="0.08"/><circle cx="18.31" cy="34.98" r="0.51" fill="white" opacity="0.15"/><circle cx="83.87" cy="39.56" r="0.67" fill="white" opacity="0.22"/><circle cx="31.89" cy="80.9" r="0.83" fill="white" opacity="0.29"/><circle cx="42.4" cy="14.62" r="0.99" fill="white" opacity="0.36"/><circle cx="79.8" cy="71.16" r="0.35" fill="white" opacity="0.43"/><circle cx="13.38" cy="54.56" r="0.51" fill="white" opacity="0.5"/><circle cx="74.15" cy="21.62" r="0.67" fill="white" opacity="0.57"/><circle cx="51.37" cy="87.59" r="0.83" fill="white" opacity="0.64"/><circle cx="23.35" cy="22.96" r="0.99" fill="white" opacity="0.08"/><circle cx="88.26" cy="51.96" r="0.35" fill="white" opacity="0.15"/><circle cx="20.2" cy="74.62" r="0.51" fill="white" opacity="0.22"/><circle cx="55.39" cy="11.38" r="0.67" fill="white" opacity="0.29"/><circle cx="72.31" cy="82.4" r="0.83" fill="white" opacity="0.36"/><circle cx="11.34" cy="41.1" r="0.99" fill="white" opacity="0.43"/><circle cx="84.8" cy="30.28" r="0.35" fill="white" opacity="0.5"/><circle cx="37.55" cy="88.36" r="0.51" fill="white" opacity="0.57"/><circle cx="33.13" cy="13.01" r="0.67" fill="white" opacity="0.64"/><circle cx="87.73" cy="66.01" r="0.83" fill="white" opacity="0.08"/><circle cx="11.07" cy="63.79" r="0.99" fill="white" opacity="0.15"/><circle cx="69.54" cy="13.25" r="0.35" fill="white" opacity="0.22"/><circle cx="60.49" cy="90.61" r="0.51" fill="white" opacity="0.29"/><circle cx="14.57" cy="26.98" r="0.67" fill="white" opacity="0.36"/><circle cx="91.99" cy="42.99" r="0.83" fill="white" opacity="0.43"/><circle cx="23.58" cy="83.77" r="0.99" fill="white" opacity="0.5"/><circle cx="46.64" cy="6.95" r="0.35" fill="white" opacity="0.57"/><circle cx="81.78" cy="79.69" r="0.51" fill="white" opacity="0.64"/><circle cx="6.21" cy="49.57" r="0.67" fill="white" opacity="0.08"/><circle cx="82.8" cy="20.53" r="0.83" fill="white" opacity="0.15"/><circle cx="45.69" cy="94.18" r="0.99" fill="white" opacity="0.22"/><circle cx="23.16" cy="14.27" r="0.35" fill="white" opacity="0.29"/><circle cx="94.22" cy="58.27" r="0.51" fill="white" opacity="0.36"/><circle cx="11.56" cy="73.93" r="0.67" fill="white" opacity="0.43"/><circle cx="62.26" cy="6.11" r="0.83" fill="white" opacity="0.5"/><circle cx="70.74" cy="90.9" r="0.99" fill="white" opacity="0.57"/></svg>
            <svg className="sphere-rings" viewBox="0 0 540 540" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
              <ellipse cx="270" cy="270" rx="250" ry="66" fill="none" stroke="rgba(94,234,212,0.18)" strokeWidth="1" />
              <ellipse cx="270" cy="270" rx="198" ry="54" fill="none" stroke="rgba(94,234,212,0.10)" strokeWidth="0.8" transform="rotate(52 270 270)" />
              <ellipse cx="270" cy="270" rx="222" ry="60" fill="none" stroke="rgba(94,234,212,0.07)" strokeWidth="0.6" transform="rotate(-34 270 270)" />
            </svg>
            <p className="sphere-name">ORBREGEN</p>
          </div>
        </div>

        <h1 className="sphere-tagline">
          Connecting Patients, Intelligence, and Experts for Better Health Care.
        </h1>

        <p className="hero-lede">
          Describe your symptoms, reach the right respiratory specialist, and get
          findings grounded in your biology — not a generic referral.
        </p>

        <div className="hero-cta">
          <a className="btn btn-primary" href="#cta">Request access <span className="arrow">→</span></a>
          <a className="btn btn-ghost" href="#cycle">See how it works</a>
        </div>

        <div className="wrap">
          <div className="hero-meta">
            <div className="stat"><div className="k">94.2<span style={{ color: "var(--slate)", fontSize: "18px" }}>%</span></div><div className="l">Anomaly recall · pilot cohort</div></div>
            <div className="stat"><div className="k">11</div><div className="l">Research partner sites</div></div>
            <div className="stat"><div className="k">2.28<span style={{ color: "var(--slate)", fontSize: "18px" }}>M</span></div><div className="l">Human lung cells in reference</div></div>
          </div>
        </div>
      </section>

      {/* CYCLE */}
      <section className="cycle wrap" id="cycle">
        <div className="section-head">
          <div>
            <span className="micro">§ 01 — The platform</span>
            <h2 className="title" style={{ marginTop: "18px" }}>
              Four layers,<br /><em>one continuous loop.</em>
            </h2>
          </div>
          <p className="sub">
            Every interaction with the platform feeds a loop that improves with use.
            Patient data sharpens specialist matching. Expert annotations refine the
            biological model. A more accurate model leads to better characterisations —
            which lead to better outcomes for everyone the platform reaches.
          </p>
        </div>

        <div className="layers">
          <article className="layer">
            <div className="num">
              <span>L · 01 / Public</span>
              <span className="badge">Patient intake</span>
            </div>
            <div className="vis" aria-hidden="true">
              <svg viewBox="0 0 320 80" width="100%" height="100%">
                <g stroke="#5EEAD4" strokeWidth="1" fill="none" opacity="0.7">
                  <rect x="10" y="22" width="180" height="14" rx="7" />
                  <rect x="10" y="44" width="120" height="14" rx="7" opacity="0.5" />
                </g>
                <circle cx="280" cy="40" r="22" fill="none" stroke="rgba(255,255,255,0.18)" />
                <circle cx="280" cy="40" r="6" fill="#5EEAD4" />
              </svg>
            </div>
            <h3>Patient connection</h3>
            <p className="desc">
              Anyone describing respiratory symptoms — without medical vocabulary or
              a referral — describes what they are experiencing. The platform triage
              conversationally and routes to the most suitable specialist based on the
              presentation.
            </p>
            <div className="bullets">
              <div><span className="b">→</span><span>Conversational triage in multiple languages</span></div>
              <div><span className="b">→</span><span>Designed for low-bandwidth and low-resource settings</span></div>
              <div><span className="b">→</span><span>Matched to a specialist based on symptom pattern</span></div>
            </div>
          </article>

          <article className="layer" style={{ background: "rgba(94,234,212,0.025)" }}>
            <div className="num">
              <span>L · 02 / Core</span>
              <span className="badge">AI Engine</span>
            </div>
            <div className="vis" aria-hidden="true">
              <svg viewBox="0 0 320 80" width="100%" height="100%">
                <path d="M0,40 Q30,10 60,40 T120,40 Q150,5 180,40 T240,40 Q270,15 300,40" stroke="#5EEAD4" strokeWidth="1.2" fill="none" />
                <circle cx="180" cy="40" r="10" fill="none" stroke="#5EEAD4" />
                <circle cx="180" cy="40" r="3" fill="#5EEAD4" />
              </svg>
            </div>
            <h3>Respiratory intelligence engine</h3>
            <p className="desc">
              Analyses each case and surfaces biological findings — which cell populations
              are out of range, which signals are unusual — so the specialist sees a precise
              picture before they even open the file. It flags deviations. It does not guess diagnoses.
            </p>
            <div className="bullets">
              <div><span className="b">→</span><span>Surfaces what is abnormal, ranked by severity</span></div>
              <div><span className="b">→</span><span>Every finding is traceable — not a black box</span></div>
              <div><span className="b">→</span><span>Available as a research API for academic use</span></div>
            </div>
          </article>

          <article className="layer">
            <div className="num">
              <span>L · 03 / Expert</span>
              <span className="badge">Expert network</span>
            </div>
            <div className="vis" aria-hidden="true">
              <svg viewBox="0 0 320 80" width="100%" height="100%">
                <g stroke="rgba(255,255,255,0.18)" fill="none">
                  <rect x="10" y="14" width="120" height="52" rx="6" />
                  <rect x="146" y="14" width="120" height="52" rx="6" />
                </g>
                <circle cx="200" cy="40" r="8" fill="none" stroke="#5EEAD4" />
                <path d="M196,40 L199,43 L204,37" stroke="#5EEAD4" strokeWidth="1.4" fill="none" />
              </svg>
            </div>
            <h3>Expert review</h3>
            <p className="desc">
              Certified respiratory physicians receive structured cases with AI-characterised
              findings. Their decisions — confirm, refine, or disagree — feed back into the
              next training cycle. Expert disagreement is the most valuable signal the system
              can receive.
            </p>
            <div className="bullets">
              <div><span className="b">→</span><span>AI-surfaced findings with full provenance</span></div>
              <div><span className="b">→</span><span>Every annotation feeds the next training run</span></div>
              <div><span className="b">→</span><span>Specialists are paid partners, not unpaid labellers</span></div>
            </div>
          </article>

          <article className="layer" style={{ opacity: 0.6 }}>
            <div className="num">
              <span>L · 04 / Future</span>
              <span className="badge" style={{ background: "rgba(255,255,255,0.06)", color: "var(--slate)" }}>In development</span>
            </div>
            <div className="vis" aria-hidden="true">
              <svg viewBox="0 0 320 80" width="100%" height="100%">
                <path d="M20,60 L80,20 L140,50 L200,30 L260,40 L300,25" stroke="rgba(94,234,212,0.4)" strokeWidth="1" fill="none" strokeDasharray="4,4"/>
                <circle cx="300" cy="25" r="6" fill="none" stroke="rgba(94,234,212,0.4)" />
              </svg>
            </div>
            <h3>Treatment intelligence</h3>
            <p className="desc">
              Because the model knows precisely what deviated and how, it can reason about
              reversal. This layer will generate evidence-based treatment directions grounded
              in the specific biological deviation — not generic protocols. It requires Layers
              2 and 3 to be fully mature first.
            </p>
            <div className="bullets">
              <div><span className="b">→</span><span>Deviation-grounded treatment directions</span></div>
              <div><span className="b">→</span><span>Pathway-targeted intervention suggestions</span></div>
              <div><span className="b">→</span><span>Drug design directions for novel mechanisms</span></div>
            </div>
          </article>
        </div>
      </section>

      {/* PATIENT (warm) */}
      <section className="patient" id="patient">
        <div className="wrap">
          <div className="section-head">
            <div>
              <span className="micro">§ 02 — Layer one · Patient intake</span>
              <h2 className="title" style={{ marginTop: "18px" }}>
                Describe what you feel.<br /><em>Reach the right specialist.</em>
              </h2>
            </div>
            <p className="sub">
              No medical vocabulary required. No referral chain needed. Anyone describing
              respiratory symptoms — in their own language, on any connection — is triaged
              conversationally and matched to the most suitable specialist based on the
              biological pattern the presentation suggests.
            </p>
          </div>

          <div className="grid">
            <div className="pcard">
              <div className="head">
                <span>orbregen.app · intake</span>
                <span>EN · हिं · বাং · தமி · 中</span>
              </div>
              <div className="body">
                <div className="chat">
                  <div className="bub user">
                    My grandfather has been coughing at night for 3 weeks.
                    There&apos;s a wheeze sometimes. He&apos;s 68.
                  </div>
                  <div className="bub ai">
                    <span className="tag">Triage · L01</span>
                    Thank you. A few quick questions: is the cough dry or
                    producing phlegm? Has he had a fever, or any chest tightness
                    when climbing stairs?
                  </div>
                  <div className="bub user">
                    Some phlegm in the morning. No fever. Yes — gets short of
                    breath on stairs.
                  </div>
                  <div className="bub ai">
                    <span className="tag">Match · L03</span>
                    Based on what you&apos;ve described, a pulmonologist is the right
                    starting point. I&apos;ve identified three specialists nearby with
                    availability today.
                  </div>
                </div>
                <div className="matched">
                  <div className="av">KM</div>
                  <div className="who">
                    <div className="n">Dr. K. Mensah</div>
                    <div className="r">Pulmonology · City Respiratory Centre · 4.2 km</div>
                  </div>
                  <div className="ok">Available 14:30</div>
                </div>
              </div>
            </div>

            <div>
              <div className="feature-list">
                <div className="feature">
                  <div className="n">01</div>
                  <div>
                    <h4>Symptoms in plain language</h4>
                    <p>Describe what you feel without medical vocabulary. The platform
                      asks the right follow-up questions conversationally — not a
                      fixed form.</p>
                  </div>
                </div>
                <div className="feature">
                  <div className="n">02</div>
                  <div>
                    <h4>Designed for any connection</h4>
                    <p>Works on 2G connections, basic phones, and SMS-based fallback.
                      No app required for first contact.</p>
                  </div>
                </div>
                <div className="feature">
                  <div className="n">03</div>
                  <div>
                    <h4>Matched to the right specialist</h4>
                    <p>Routing is based on the biological pattern the symptoms suggest —
                      not a generic referral. Matched by presentation, location, and
                      specialist focus.</p>
                  </div>
                </div>
                <div className="feature">
                  <div className="n">04</div>
                  <div>
                    <h4>Privacy by default</h4>
                    <p>End-to-end encrypted from intake. Patient data is never used
                      for model training without explicit, revocable consent.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ENGINE (dark) */}
      <section className="engine noise" id="engine">
        <div className="wrap">
          <div className="section-head">
            <div>
              <span className="micro">§ 03 — Layer two · AI engine</span>
              <h2 className="title" style={{ marginTop: "18px" }}>
                The AI that reads<br /><em>your biology.</em>
              </h2>
            </div>
            <p className="sub">
              Every case is analysed against a reference of what a healthy respiratory
              system looks like. The engine flags what is out of range — which cells,
              which signals, which processes — and hands that picture to a specialist.
              They see the deviation. They make the call.
            </p>
          </div>

          <div className="grid">
            <div className="console">
              <div className="head">
                <span>ORBREGEN ENGINE · DEVIATION ANALYSIS</span>
                <span className="live"><span className="d"></span>ACTIVE</span>
              </div>
              <div className="body">
                <div className="scope">
                  <div className="gridlines"></div>
                  <svg viewBox="0 0 600 200" preserveAspectRatio="none">
                    <defs>
                      <linearGradient id="pos" x1="0" x2="1">
                        <stop offset="0%" stopColor="#5EEAD4" stopOpacity="0.9"/>
                        <stop offset="100%" stopColor="#5EEAD4" stopOpacity="0.5"/>
                      </linearGradient>
                      <linearGradient id="neg" x1="1" x2="0">
                        <stop offset="0%" stopColor="#94A3B8" stopOpacity="0.6"/>
                        <stop offset="100%" stopColor="#94A3B8" stopOpacity="0.2"/>
                      </linearGradient>
                    </defs>
                    {/* Reference line */}
                    <line x1="200" y1="0" x2="200" y2="200" stroke="rgba(255,255,255,0.15)" strokeWidth="1.5" strokeDasharray="5,5"/>
                    {/* AT2 cells: +2.8σ */}
                    <rect x="200" y="18" width="140" height="22" rx="3" fill="url(#pos)"/>
                    {/* Macrophages: +1.9σ */}
                    <rect x="200" y="52" width="95" height="22" rx="3" fill="url(#pos)" opacity="0.65"/>
                    {/* Club cells: −0.4σ */}
                    <rect x="180" y="86" width="20" height="22" rx="3" fill="rgba(255,255,255,0.18)"/>
                    {/* Basal cells: −3.1σ */}
                    <rect x="44" y="120" width="156" height="22" rx="3" fill="url(#neg)"/>
                    {/* Endothelial: −1.2σ */}
                    <rect x="140" y="154" width="60" height="22" rx="3" fill="rgba(255,255,255,0.15)"/>
                  </svg>
                  <div className="anomaly" style={{ top: "9%", left: "56%" }}></div>
                  <div className="anomaly" style={{ top: "60%", left: "7%", width: "10px", height: "10px", borderColor: "rgba(148,163,184,0.7)" }}></div>
                  <span className="label-line" style={{ top: "5%", left: "58%" }}>↳ AT2 cells · +2.8σ</span>
                  <span className="label-line" style={{ top: "57%", left: "8%", color: "var(--slate)" }}>Basal cells · −3.1σ</span>
                </div>
                <div className="metrics">
                  <div className="metric">
                    <div className="v">94.2<span style={{ fontSize: "16px", color: "var(--slate)" }}>%</span></div>
                    <div className="l">Anomaly recall</div>
                  </div>
                  <div className="metric">
                    <div className="v">2.28<span style={{ fontSize: "16px", color: "var(--slate)" }}>M</span></div>
                    <div className="l">Cells in reference</div>
                  </div>
                  <div className="metric">
                    <div className="v">55<span style={{ fontSize: "16px", color: "var(--slate)" }}>K</span></div>
                    <div className="l">Genes profiled per cell</div>
                  </div>
                </div>
              </div>
            </div>

            <div>
              <div className="capabilities">
                <div className="cap">
                  <div className="n">A.01</div>
                  <div className="t">
                    Cell-type deviation analysis
                    <small>Which populations are expanded or depleted versus the healthy reference — computed at gene resolution across 55,329 genes.</small>
                  </div>
                  <div className="a">→</div>
                </div>
                <div className="cap">
                  <div className="n">A.02</div>
                  <div className="t">
                    Traced, not opaque
                    <small>Every flagged deviation links to the source Z-score in the reference model. The gene, the cell type, the statistical basis — all inspectable.</small>
                  </div>
                  <div className="a">→</div>
                </div>
                <div className="cap">
                  <div className="n">A.03</div>
                  <div className="t">
                    Biological pathway characterisation
                    <small>Dysregulated processes identified from the gene deviation profile. No hardcoded pathway lists — everything is computed from the data.</small>
                  </div>
                  <div className="a">→</div>
                </div>
                <div className="cap">
                  <div className="n">A.04</div>
                  <div className="t">
                    Open research API
                    <small>Available to academic partners under a data-use agreement. Free for non-commercial publications. Reproducibility is built in.</small>
                  </div>
                  <div className="a">→</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CLINICIAN */}
      <section className="clinic" id="clinic">
        <div className="wrap">
          <div className="section-head">
            <div>
              <span className="micro">§ 04 — Layer three · Expert network</span>
              <h2 className="title" style={{ marginTop: "18px" }}>
                Findings, not conclusions —<br />judgment stays with the <em>clinician.</em>
              </h2>
            </div>
            <p className="sub">
              Certified physicians receive structured cases — not raw inboxes. Each case
              surfaces the AI-characterised findings alongside the original signal, with
              provenance and confidence on every claim. Annotations and corrections feed
              directly into the next training cycle, closing the loop that makes the model
              more accurate over time.
            </p>
          </div>

          <div className="grid">
            <div>
              <div className="clin-points">
                <div className="clp">
                  <h4>Structured cases, ranked by urgency</h4>
                  <p>A triaged queue with patient context, AI-characterised cell-type
                    deviations, and the gene-level evidence behind each finding.
                    Provenance is attached to every claim.</p>
                </div>
                <div className="clp">
                  <h4>Annotation as a first-class action</h4>
                  <p>Confirm, refine, or disagree. Every clinician decision is captured
                    as structured supervision and feeds directly into the next training run.
                    Disagreement is the most precise signal.</p>
                </div>
                <div className="clp">
                  <h4>Compensation for contribution</h4>
                  <p>Time spent reviewing and annotating is paid time. Specialists are
                    partners in the model — not unpaid labellers. The compensation
                    reflects that.</p>
                </div>
              </div>
            </div>

            <div className="case">
              <div className="head">
                <span className="id">CASE · 24-A881 · PUL</span>
                <span className="stat"><span className="d"></span>AI · REVIEW READY</span>
              </div>
              <div className="body">
                <div className="pane">
                  <div className="pl">Cell composition · 847 cells profiled</div>
                  <svg viewBox="0 0 240 90" width="100%" height="80">
                    <g fontFamily="'Geist Mono', monospace" fontSize="8">
                      <text x="4" y="20" fill="rgba(255,255,255,0.45)">AT2</text>
                      <rect x="30" y="12" width="110" height="8" rx="1" fill="#5EEAD4" opacity="0.7"/>
                      <text x="144" y="20" fill="#5EEAD4">+2.8σ</text>
                      <text x="4" y="40" fill="rgba(255,255,255,0.45)">MΦ</text>
                      <rect x="30" y="32" width="74" height="8" rx="1" fill="#5EEAD4" opacity="0.5"/>
                      <text x="108" y="40" fill="#5EEAD4">+1.9σ</text>
                      <text x="4" y="60" fill="rgba(255,255,255,0.45)">BAS</text>
                      <rect x="30" y="52" width="124" height="8" rx="1" fill="rgba(148,163,184,0.5)"/>
                      <text x="158" y="60" fill="rgba(148,163,184,0.8)">−3.1σ</text>
                      <text x="4" y="80" fill="rgba(255,255,255,0.25)">END</text>
                      <rect x="30" y="72" width="46" height="8" rx="1" fill="rgba(255,255,255,0.2)"/>
                      <text x="80" y="80" fill="rgba(255,255,255,0.3)">−1.2σ</text>
                    </g>
                  </svg>
                </div>
                <div className="pane" style={{ position: "relative" }}>
                  <div className="pl">Top gene deviations · 12 outside reference</div>
                  <div style={{ padding: "8px 0 4px", display: "flex", flexDirection: "column", gap: "5px" }}>
                    {[
                      ["SFTPC", "+4.2σ", "#5EEAD4"],
                      ["MMP12", "+3.7σ", "#5EEAD4"],
                      ["TP63",  "−3.1σ", "rgba(148,163,184,0.8)"],
                      ["FOXJ1", "−2.8σ", "rgba(148,163,184,0.8)"],
                    ].map(([gene, score, color]) => (
                      <div key={gene} style={{ display: "flex", justifyContent: "space-between", fontFamily: "'Geist Mono', monospace", fontSize: "10px" }}>
                        <span style={{ color: "rgba(255,255,255,0.55)" }}>{gene}</span>
                        <span style={{ color }}>{score}</span>
                      </div>
                    ))}
                  </div>
                  <span style={{ position: "absolute", bottom: "10px", right: "12px", fontFamily: "'Geist Mono',monospace", fontSize: "9px", letterSpacing: "0.14em", color: "var(--teal)" }}>
                    ↳ scVI · 4 pathways flagged
                  </span>
                </div>
              </div>
              <div className="findings">
                <div className="find">
                  <span className="nm">AT2 CELLS</span>
                  <span className="bar"><i style={{ width: "91%" }}></i></span>
                  <span className="pct">+2.8σ</span>
                </div>
                <div className="find">
                  <span className="nm">MACROPHAG.</span>
                  <span className="bar"><i style={{ width: "61%" }}></i></span>
                  <span className="pct">+1.9σ</span>
                </div>
                <div className="find">
                  <span className="nm">BASAL CELLS</span>
                  <span className="bar"><i style={{ width: "100%", background: "var(--slate)" }}></i></span>
                  <span className="pct" style={{ color: "var(--slate)" }}>−3.1σ</span>
                </div>
              </div>
              <div className="actions">
                <button className="b primary">Confirm findings</button>
                <button className="b">Refine</button>
                <button className="b">Disagree</button>
                <button className="b" style={{ marginLeft: "auto" }}>Open full case ↗</button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* TRUST */}
      <section className="trust" id="trust">
        <div className="wrap">
          <div className="row">
            <div>
              <span className="micro">§ 05 — Research & trust</span>
              <h2 className="title" style={{ marginTop: "18px", fontSize: "42px" }}>
                Built with the rigour<br /><em>clinical medicine demands.</em>
              </h2>
              <p style={{ marginTop: "20px", fontSize: "15px", lineHeight: "1.7", color: "var(--slate)", maxWidth: "460px" }}>
                ORBREGEN is in clinical preview with eleven research partner sites —
                pulmonology groups, hospital systems, and academic institutions across
                multiple continents. Partner identities are shared under NDA for institutions
                evaluating the platform.
              </p>
              <div className="compliance">
                <span className="badge2">HIPAA · in progress</span>
                <span className="badge2">GDPR · in progress</span>
                <span className="badge2">ISO 13485</span>
                <span className="badge2">SOC 2 · type II</span>
                <span className="badge2">FDA · pre-submission</span>
              </div>
            </div>
            <div className="lo">
              <div className="it">Pulmonology<br />groups</div>
              <div className="it">Hospital<br />systems</div>
              <div className="it">Academic<br />research labs</div>
              <div className="it">Rural-care<br />networks</div>
              <div className="it">11<br />partner sites</div>
              <div className="it">Multiple<br />continents</div>
              <div className="it">Clinical<br />preview · active</div>
              <div className="it">Expanding<br />access · 2026</div>
            </div>
          </div>
        </div>
      </section>

      {/* PHILOSOPHY */}
      <section className="philosophy" id="philosophy">
        <div className="wrap">
          <div className="philosophy-intro">
            <span className="micro">§ 06 — Philosophy</span>
            <p className="philosophy-lead">We built this on a single, unfashionable belief.</p>
            <p className="philosophy-statement">
              If a system truly understands what <em>healthy</em> looks like,<br />disease explains itself.
            </p>
          </div>

          <div className="philosophy-pillars">
            <div className="pillar">
              <span className="pn">01</span>
              <h3>The model must learn from life, not from rules</h3>
              <p>Biology is too complex for manually curated signatures. Every reference in ORBREGEN comes from real human cells — 2.28 million of them across donors, tissues, and conditions. The statistics are computed from the data, not assumed by a researcher.</p>
            </div>
            <div className="pillar">
              <span className="pn">02</span>
              <h3>Description comes before diagnosis</h3>
              <p>The system characterises what it observes: which cell populations are shifted, which genes deviate, which processes are dysregulated. It does not reach for a disease name. That reasoning belongs to a clinician with full context — not an algorithm with a lookup table.</p>
            </div>
            <div className="pillar">
              <span className="pn">03</span>
              <h3>Access is not a feature — it is the mission</h3>
              <p>The same intelligence that serves a research lab should be reachable by anyone, anywhere in the world. If the platform is only useful to the well-resourced, it has not solved the problem — it has redecorated it.</p>
            </div>
            <div className="pillar">
              <span className="pn">04</span>
              <h3>Disagreement is the most valuable signal</h3>
              <p>When a clinician corrects the model, that correction is not a failure — it is the most precise training data the system can receive. The flywheel runs on expert disagreement captured at scale. We pay for that disagreement, because it is worth more than agreement.</p>
            </div>
            <div className="pillar">
              <span className="pn">05</span>
              <h3>Treatment follows understanding</h3>
              <p>You cannot know how to correct something until you know precisely what deviated and why. The path to treatment intelligence runs through biological clarity — not through naming conditions, but through characterising their mechanisms with enough precision to reverse them.</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="cta noise" id="cta">
        <div className="wrap">
          <span className="micro">§ 07 — Begin</span>
          <h2 style={{ marginTop: "18px" }}>
            Join the clinical<br /><em>preview.</em>
          </h2>
          <p>
            ORBREGEN is in clinical preview with eleven research partners.
            We are opening access to pulmonology groups, hospital systems, and
            rural-care networks progressively through 2026.
          </p>
          <div className="cta-paths">
            <a className="path" href="#">
              <div className="l">Clinical preview</div>
              <h3>Request clinical access</h3>
              <p>
                Onboard your specialists and start receiving structured,
                AI-characterised cases as part of the preview programme.
                We respond within five business days.
              </p>
              <span className="go">Apply for access <span className="arrow">→</span></span>
            </a>
            <a className="path" href="#">
              <div className="l">Research access</div>
              <h3>Access the AI engine</h3>
              <p>
                The ORBREGEN AI engine is available to academic partners under a
                data-use agreement. Free for non-commercial publications.
                Reproducibility is built in.
              </p>
              <span className="go">Read the API docs <span className="arrow">→</span></span>
            </a>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer>
        <div className="wrap">
          <div className="grid">
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
                Biological intelligence connecting patients, clinicians, and
                the research community — starting with respiratory.
              </p>
            </div>
            <div>
              <h5>Platform</h5>
              <ul>
                <li><a href="#patient">Patient intake</a></li>
                <li><a href="#clinic">Expert network</a></li>
                <li><a href="#engine">AI Engine</a></li>
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
