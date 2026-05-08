import NavBar from '../components/NavBar';

export default function VisionPage() {
  return (
    <>
      <NavBar active="vision" />

      {/* HERO */}
      <section className="vm-hero noise">
        <div className="wrap">
          <div className="vm-hero-inner">
            <span className="micro">Vision &amp; Mission</span>
            <h1 className="vm-hero-h1">
              A world where every body is understood<br /><em>before it breaks down.</em>
            </h1>
            <p className="vm-hero-sub">
              We are building a biological intelligence system capable of reading any human body
              at cellular resolution — detecting deviation from healthy, connecting patients to
              the right expertise, and eventually guiding the correction of what has gone wrong.
              We are starting with the lung.
            </p>
          </div>
        </div>
      </section>

      {/* THE PROBLEM */}
      <section className="vm-problem">
        <div className="wrap">
          <div className="vm-problem-grid">
            <div>
              <span className="micro">The problem</span>
              <h2 className="about-section-title" style={{ marginTop: "24px" }}>
                Medicine today is<br />symptom-matching.<br /><em>It should be biology-reading.</em>
              </h2>
              <p style={{ marginTop: "28px", fontSize: "16px", lineHeight: "1.75", color: "var(--slate)", textWrap: "pretty", maxWidth: "480px" }}>
                By the time symptoms appear, the underlying biology has often already shifted —
                cell populations have changed, gene expression has drifted, pathways have been
                altered for months or years. Current diagnostics surface patterns from what
                patients describe. We are building a system that reads what cells show.
              </p>
              <p style={{ marginTop: "18px", fontSize: "16px", lineHeight: "1.75", color: "var(--slate)", textWrap: "pretty", maxWidth: "480px" }}>
                The gap between symptom-onset and cellular-onset is where early detection lives.
                That is the gap we are closing.
              </p>
            </div>
            <div className="vm-problem-stats">
              <div className="vm-stat">
                <div className="vm-stat-n">4.7<span>M</span></div>
                <div className="vm-stat-l">
                  People die annually from chronic respiratory diseases — the vast majority in
                  low- and middle-income countries where specialist access is structurally limited.
                </div>
              </div>
              <div className="vm-stat">
                <div className="vm-stat-n">2–5<span>yr</span></div>
                <div className="vm-stat-l">
                  Average delay between first symptoms and correct diagnosis for rare or complex
                  lung diseases — during which irreversible damage accumulates.
                </div>
              </div>
              <div className="vm-stat">
                <div className="vm-stat-n">~60<span>%</span></div>
                <div className="vm-stat-l">
                  Of first-contact respiratory referrals do not reach the right sub-specialist —
                  routed by symptom pattern, not biological profile.
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* VISION */}
      <section className="vm-vision noise">
        <div className="wrap">
          <span className="micro">The vision</span>
          <p className="vm-vision-quote">
            &ldquo;Every patient, understood at cellular resolution — regardless of where they
            live, who they can afford to see, or what their symptoms sound like.&rdquo;
          </p>
          <div className="vm-vision-body">
            <div className="vm-vision-col">
              <h3>A complete map of healthy human biology</h3>
              <p>
                The long-term goal is a reference model of every organ system in the human body —
                built from real human cells, computed from data, and refined by expert feedback.
                Not a textbook summary. A statistical model with enough resolution to detect
                cellular-level deviation in any sample from any donor.
              </p>
              <p>
                This reference does not exist yet. Pieces of it exist — the Human Lung Cell Atlas
                is the most advanced of them. We are using it to build the first production-grade
                implementation of what a full-body reference could look like.
              </p>
            </div>
            <div className="vm-vision-col">
              <h3>Intelligence accessible to anyone, anywhere</h3>
              <p>
                A patient in a rural clinic should have access to the same biological intelligence
                as a patient at a major academic medical centre. The bottleneck is not physician
                count — it is the absence of a system that can process biology and route patients
                to the right expertise at scale.
              </p>
              <p>
                That system is what we are building. It is not a telemedicine platform. It is an
                intelligence layer that reads biology, informs specialists, and scales in ways that
                physician networks cannot.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* MISSION */}
      <section className="vm-mission">
        <div className="wrap">
          <span className="micro">The mission</span>
          <h2 className="about-section-title" style={{ marginTop: "24px" }}>
            Build the reference.<br />Detect the deviation.<br />Connect the expertise.
          </h2>
          <div className="vm-mission-cards">
            <div className="vm-mission-card">
              <div className="vm-mission-card-n">01 — Reference</div>
              <h3>Build the world&apos;s most detailed model of healthy human biology</h3>
              <p>
                Starting with the lung — 2.28 million cells, 55,329 genes, 16 disease states
                present for validation. Every reference statistic computed from the data.
                Nothing hardcoded. The model learns what healthy looks like at every level of
                resolution: gene, cell type, tissue region, donor variation.
              </p>
              <span className="vm-mission-current">Active — respiratory</span>
            </div>
            <div className="vm-mission-card">
              <div className="vm-mission-card-n">02 — Detection</div>
              <h3>Surface every deviation from healthy with full biological traceability</h3>
              <p>
                When a sample arrives, the model compares it against the reference and describes
                every deviation — which cell populations are expanded or depleted, which genes
                are out of range, which biological pathways are dysregulated. The model does not
                name diseases. It characterises biology. Experts name diseases.
              </p>
            </div>
            <div className="vm-mission-card">
              <div className="vm-mission-card-n">03 — Connection</div>
              <h3>Connect patients to the right expertise, grounded in their biology</h3>
              <p>
                Patient matching is not keyword search. It is the deviation profile from the AI
                engine mapped to the expertise profile of a certified specialist. The right match
                is not the nearest pulmonologist — it is the one whose case experience best fits
                the biological pattern present in this patient&apos;s data.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* FOUR LAYERS */}
      <section className="vm-layers">
        <div className="wrap">
          <span className="micro">The architecture</span>
          <h2 className="about-section-title" style={{ marginTop: "24px" }}>
            Four layers.<br />One connected system.
          </h2>
          <div className="vm-layers-list">

            <div className="vm-layer">
              <div className="vm-layer-num">1</div>
              <div>
                <div className="vm-layer-label">Patient connection</div>
                <h3 className="vm-layer-title">The face of the platform</h3>
                <div className="vm-layer-who">Who — Any citizen</div>
                <span className="vm-layer-tag">Phase 2</span>
              </div>
              <div className="vm-layer-body">
                <p>
                  Any person with a concern describes their symptoms, duration, and history in
                  plain language. No medical background required. The platform processes the intake
                  and matches them with the most suitable specialist for their specific presentation
                  — not a generic referral, but a match based on the biological deviation pattern
                  their symptoms suggest.
                </p>
                <p>
                  The intelligence behind the matching comes from Layer 2. Layer 1 is the interface
                  through which that intelligence reaches patients. It is designed for anyone,
                  anywhere — including low-bandwidth and low-resource settings where specialist
                  access is structurally limited.
                </p>
              </div>
            </div>

            <div className="vm-layer">
              <div className="vm-layer-num">2</div>
              <div>
                <div className="vm-layer-label">AI intelligence engine</div>
                <h3 className="vm-layer-title">The biological reference model</h3>
                <div className="vm-layer-who">Who — Research laboratories · powers Layer 1</div>
                <span className="vm-layer-tag active">Active — Phase 1</span>
              </div>
              <div className="vm-layer-body">
                <p>
                  The core of the platform. A biological model built from 2.28 million human lung
                  cells across the Human Lung Cell Atlas — profiling what healthy human biology
                  looks like at the level of individual cells, gene by gene, tissue region by
                  tissue region. The lung is where we start. The method applies to every organ.
                </p>
                <p>
                  When a new sample arrives, the model compares it against this reference and
                  surfaces every deviation: which cell populations are expanded or depleted, which
                  genes are outside their normal distribution, which biological pathways are showing
                  abnormal activation. It returns Z-scores, deviation magnitudes, and pathway states
                  — not disease names. Clinical judgment belongs to the expert in Layer 3.
                </p>
                <p>
                  This layer is the first we are building. It is currently in research preview with
                  eleven partner sites. API access is available for non-commercial research under a
                  data-use agreement.
                </p>
              </div>
            </div>

            <div className="vm-layer">
              <div className="vm-layer-num">3</div>
              <div>
                <div className="vm-layer-label">Expert network</div>
                <h3 className="vm-layer-title">The feedback flywheel</h3>
                <div className="vm-layer-who">Who — Certified physicians · Starting with respiratory specialists</div>
                <span className="vm-layer-tag">Phase 3</span>
              </div>
              <div className="vm-layer-body">
                <p>
                  Certified physicians — starting with respiratory specialists — interact with the
                  model&apos;s findings. They review the deviations surfaced by Layer 2, confirm or
                  correct them, add clinical context, and contribute annotated cases back to the
                  training data. As the reference expands to new organ systems, so does the network.
                </p>
                <p>
                  Each expert interaction makes the model more accurate and more specific. Better
                  model output leads to better patient matching leads to more expert engagement
                  leads to better model. This is the flywheel that makes the platform progressively
                  more valuable as it scales — not a static tool that plateaus, but a system that
                  compounds.
                </p>
              </div>
            </div>

            <div className="vm-layer">
              <div className="vm-layer-num">4</div>
              <div>
                <div className="vm-layer-label">Treatment intelligence</div>
                <h3 className="vm-layer-title">The destination</h3>
                <div className="vm-layer-who">Who — Clinicians · Researchers · Drug developers</div>
                <span className="vm-layer-tag">Phase 4 — Future</span>
              </div>
              <div className="vm-layer-body">
                <p>
                  Because the model knows what healthy looks like and can precisely describe what
                  has broken down, it can reason about how to reverse the breakdown. Layer 4
                  generates evidence-based treatment directions grounded in the specific biological
                  deviation — not generic protocols derived from population averages.
                </p>
                <p>
                  For known mechanisms, the model surfaces targeted interventions ranked by target
                  quality and evidence. For novel or poorly understood patterns, it characterises
                  the mechanism in a form that can inform drug design. This layer does not exist
                  yet. It is powered by Layers 2 and 3 being sufficiently mature — and it is the
                  reason we are building in sequence.
                </p>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* ROADMAP */}
      <section className="vm-roadmap">
        <div className="wrap">
          <span className="micro">The roadmap</span>
          <h2 className="about-section-title" style={{ marginTop: "24px" }}>
            Built in sequence.<br />Each layer depends on the one before it.
          </h2>
          <div className="vm-roadmap-phases">
            <div className="vm-phase">
              <div className="vm-phase-n">Phase 1</div>
              <h3>Respiratory Intelligence Engine</h3>
              <p>
                Build the healthy reference model from 2.28 million HLCA cells. Validate anomaly
                detection. Expose via research API for lab partners. Build the evidence base before
                the interface.
              </p>
              <span className="vm-phase-status active">In progress</span>
            </div>
            <div className="vm-phase">
              <div className="vm-phase-n">Phase 2</div>
              <h3>Patient Portal</h3>
              <p>
                Patient intake and specialist matching powered by the Layer 2 model. Symptom
                description → biological deviation profile → matched specialist. Initially
                respiratory; expands with the reference model.
              </p>
              <span className="vm-phase-status next">Next</span>
            </div>
            <div className="vm-phase">
              <div className="vm-phase-n">Phase 3</div>
              <h3>Expert Network</h3>
              <p>
                Certified physicians review model findings, annotate cases, and contribute to
                model improvement. Structured feedback loop that makes the model progressively
                more accurate and specific over time.
              </p>
              <span className="vm-phase-status future">Planned</span>
            </div>
            <div className="vm-phase">
              <div className="vm-phase-n">Phase 4</div>
              <h3>Treatment Intelligence</h3>
              <p>
                Given a precise deviation profile and a mature expert-validated model, reason
                about how to reverse the breakdown. Treatment directions grounded in the specific
                biology, not population averages or generic protocols.
              </p>
              <span className="vm-phase-status future">Future</span>
            </div>
          </div>
        </div>
      </section>

      {/* BELIEFS */}
      <section className="vm-beliefs">
        <div className="wrap">
          <span className="micro">What we believe</span>
          <h2 className="about-section-title" style={{ marginTop: "24px" }}>
            The principles that hold<br />through every decision.
          </h2>
          <div className="vm-beliefs-grid">
            <div className="vm-belief">
              <div className="vm-belief-n">I</div>
              <h3>Compute what others curate</h3>
              <p>
                No curated gene lists. No manually written disease signatures. No expert opinion
                baked into the reference. Every statistic the model holds is computed from real
                human cell data. If we cannot derive it from the data, we do not make it. This is
                not a methodological preference — it is the only way to build a model that can be
                systematically extended and verified.
              </p>
            </div>
            <div className="vm-belief">
              <div className="vm-belief-n">II</div>
              <h3>Describe biology. Defer naming.</h3>
              <p>
                The model returns deviations. Experts name diseases. This boundary is load-bearing.
                A model that returns diagnosis strings has taken on liability it cannot carry — one
                that will be wrong in ways that cannot be traced or corrected. We describe what
                the cells show. We do not tell clinicians what to conclude from it. That judgment
                is theirs and always will be.
              </p>
            </div>
            <div className="vm-belief">
              <div className="vm-belief-n">III</div>
              <h3>Build the flywheel before the product</h3>
              <p>
                Layer 2 before Layer 1. Reference before matching. Understanding before treatment.
                There is a temptation to build the patient-facing interface first because it is
                more legible to investors and the public. We resist it. A patient-matching product
                is only as good as the biological model it sits on top of. We build in sequence.
              </p>
            </div>
            <div className="vm-belief">
              <div className="vm-belief-n">IV</div>
              <h3>Healthy before disease</h3>
              <p>
                The reference model is built exclusively from cells labelled normal. We do not
                train on disease cells — we reserve them for validation. This is the methodological
                insight at the centre of everything: a system that deeply understands healthy can
                detect any deviation from it without being told what diseases to look for. The
                reference is the asset.
              </p>
            </div>
            <div className="vm-belief">
              <div className="vm-belief-n">V</div>
              <h3>Traceability is not optional</h3>
              <p>
                Every flagged finding must be traceable to the source statistics. Clinicians can
                inspect the specific cell-type deviation, the gene-level Z-scores, and the pathway
                activation that drove any given output. A model that cannot explain its findings to
                a clinician is a model that cannot be trusted in a clinical setting. We build to be
                audited, not trusted blindly.
              </p>
            </div>
            <div className="vm-belief">
              <div className="vm-belief-n">VI</div>
              <h3>Respiratory is the start, not the scope</h3>
              <p>
                The Human Lung Cell Atlas gave us the data to begin. The clinical need was clear.
                The method we have built does not depend on the lung — it depends on having a
                high-quality cell atlas to build from. As atlases for other organ systems mature,
                we expand. The architecture is organ-agnostic. The mission is full-body biological
                intelligence.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="vm-cta noise">
        <div className="wrap">
          <h2>
            Be part of<br /><em>the reference.</em>
          </h2>
          <p>
            We are working with research institutions, pulmonology groups, and hospital systems.
            Clinical preview is open. If you want early access, reach out directly.
          </p>
          <div className="vm-cta-actions">
            <a className="btn btn-primary" href="/#cta">Request access <span className="arrow">→</span></a>
            <a className="btn btn-ghost" href="/about">About us</a>
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
                <li><a href="/vision">Vision &amp; Mission</a></li>
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
