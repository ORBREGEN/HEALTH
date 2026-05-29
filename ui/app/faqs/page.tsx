import NavBar from '../components/NavBar';

export default function FaqsPage() {
  return (
    <>
      <NavBar active="faqs" />

      {/* HERO */}
      <section className="faq-hero">
        <div className="wrap">
          <span className="micro">Frequently asked questions</span>
          <h1 className="about-headline" style={{ marginTop: "28px", maxWidth: "640px" }}>
            Everything you need<br />to <em>understand Senebiclabs.</em>
          </h1>
        </div>
      </section>

      {/* FAQ BODY */}
      <div className="faq-body">
        <div className="wrap">
          <div className="faq-layout">

            {/* SIDEBAR NAV */}
            <nav className="faq-nav">
              <a href="#the-platform">The platform</a>
              <a href="#the-model">The model</a>
              <a href="#for-patients">For patients</a>
              <a href="#for-clinicians">For clinicians</a>
              <a href="#privacy">Privacy & security</a>
              <a href="#access">Access & pricing</a>
            </nav>

            {/* FAQ GROUPS */}
            <div className="faq-groups">

              <section className="faq-group" id="the-platform">
                <h2 className="faq-group-title">The platform</h2>
                <div className="faq-list">
                  <details className="faq-item">
                    <summary className="faq-q">What is Senebiclabs?</summary>
                    <div className="faq-a">
                      <p>Senebiclabs is a biological intelligence platform built across four interconnected layers: a patient intake and matching system, a detection engine built from human cell data, an expert network of certified physicians, and a treatment intelligence layer currently in development.</p>
                      <p>The platform is built on a single insight, if a system deeply understands what a healthy human body looks like at the cellular level, it can detect anything that deviates from that, and eventually guide its correction. We are starting with the respiratory system.</p>
                    </div>
                  </details>
                  <details className="faq-item">
                    <summary className="faq-q">Who is Senebiclabs for?</summary>
                    <div className="faq-a">
                      <p>The platform serves three groups simultaneously:</p>
                      <ul>
                        <li><strong>Patients</strong>, anyone who needs to describe respiratory symptoms and be matched to the right specialist, including those in low-bandwidth or low-resource settings.</li>
                        <li><strong>Clinicians</strong>, certified respiratory physicians who review model-flagged findings, annotate cases, and contribute to model improvement.</li>
                        <li><strong>Researchers</strong>, academic and clinical research teams who access the detection engine via the research API for non-commercial work.</li>
                      </ul>
                    </div>
                  </details>
                  <details className="faq-item">
                    <summary className="faq-q">Is the platform available to the public?</summary>
                    <div className="faq-a">
                      <p>Senebiclabs is currently in development. We are building toward access for pulmonology groups, hospital systems, and rural-care networks. To express interest in early access, use the form on the main page.</p>
                    </div>
                  </details>
                  <details className="faq-item">
                    <summary className="faq-q">What is the four-layer architecture?</summary>
                    <div className="faq-a">
                      <p><strong>Layer 1, Patient connection.</strong> Any citizen describes symptoms in plain language and is matched to the most suitable respiratory specialist for their presentation.</p>
                      <p><strong>Layer 2, Detection engine.</strong> A biological model built from the Human Lung Cell Atlas. It learns what a healthy human body looks like at the cellular level, starting with the lung, and describes deviations from that baseline.</p>
                      <p><strong>Layer 3, Expert network.</strong> Certified physicians review model findings, confirm deviations, add clinical context, and contribute annotated cases back to training data.</p>
                      <p><strong>Layer 4, Treatment intelligence.</strong> Currently in development. Will generate evidence-based treatment directions grounded in the biological deviation, not generic protocols.</p>
                    </div>
                  </details>
                </div>
              </section>

              <section className="faq-group" id="the-model">
                <h2 className="faq-group-title">The model</h2>
                <div className="faq-list">
                  <details className="faq-item">
                    <summary className="faq-q">What data was the model trained on?</summary>
                    <div className="faq-a">
                      <p>The reference model is built exclusively from the Human Lung Cell Atlas — a large-scale collection of real human lung cells across donors, tissues, and conditions. The model learns only from cells labelled <em>normal</em>. Disease cells are reserved for validation and expert training data, never for building the reference.</p>
                      <p>The atlas spans multiple disease states and profiles gene expression per cell across five levels of cell-type granularity. Every reference statistic is computed from this data, nothing is manually curated or hardcoded.</p>
                    </div>
                  </details>
                  <details className="faq-item">
                    <summary className="faq-q">Does Senebiclabs diagnose diseases?</summary>
                    <div className="faq-a">
                      <p>No. This is a hard constraint, not a limitation. The model characterises biology, it describes which cell populations are expanded or depleted, which genes are outside their normal range, and which biological processes are dysregulated.</p>
                      <p>It does not name diseases. Diseases emerge from the pattern. The naming and clinical judgment belong to the expert in Layer 3. Every output from the API returns deviations, Z-scores, and pathway states, not diagnosis strings.</p>
                    </div>
                  </details>
                  <details className="faq-item">
                    <summary className="faq-q">How accurate is the anomaly detection?</summary>
                    <div className="faq-a">
                      <p>The model is currently in active development and has not yet been validated against clinical cohorts. Validation against real patient data is a prerequisite before any clinical use, and that work is part of the roadmap. Every output from the engine is intended for research review, not clinical decision-making at this stage.</p>
                    </div>
                  </details>
                  <details className="faq-item">
                    <summary className="faq-q">Is the model a black box?</summary>
                    <div className="faq-a">
                      <p>No. Every flagged finding is traceable to the source statistics in the reference model. Clinicians can inspect the specific cell-type deviation, the gene-level Z-scores, and the biological pathway activation that drove any given output. The model is built to be audited, not trusted blindly.</p>
                    </div>
                  </details>
                  <details className="faq-item">
                    <summary className="faq-q">What technology underpins the model?</summary>
                    <div className="faq-a">
                      <p>The model uses scVI, the pre-trained HLCA reference model, for embedding and representation. Analysis is built with scanpy and anndata. All large datasets are accessed in read-only mode to avoid loading 20 GB files into RAM. The API layer runs on FastAPI with Pydantic v2 for data validation.</p>
                    </div>
                  </details>
                </div>
              </section>

              <section className="faq-group" id="for-patients">
                <h2 className="faq-group-title">For patients</h2>
                <div className="faq-list">
                  <details className="faq-item">
                    <summary className="faq-q">How does patient intake work?</summary>
                    <div className="faq-a">
                      <p>A patient describes their symptoms, duration, and history in plain language, no medical vocabulary required. The platform asks the right follow-up questions conversationally, then matches the patient to the most suitable respiratory specialist based on the type of deviation their presentation suggests.</p>
                      <p>This is not a generic referral. The match is based on the specific biological pattern indicated, the patient&apos;s location, language, and the specialist&apos;s focus area.</p>
                    </div>
                  </details>
                  <details className="faq-item">
                    <summary className="faq-q">What languages are supported?</summary>
                    <div className="faq-a">
                      <p>Conversational triage is designed to work in multiple languages. The platform is built with access in mind, intended for anyone describing respiratory symptoms, including those in low-bandwidth or low-resource settings without access to specialist care through conventional referral chains.</p>
                    </div>
                  </details>
                  <details className="faq-item">
                    <summary className="faq-q">Does it work on low-bandwidth connections?</summary>
                    <div className="faq-a">
                      <p>Yes. The patient intake layer is designed to work on 2G connections and basic smartphones. No app is required for first contact. An SMS-based fallback is available for initial triage where data connections are unreliable.</p>
                    </div>
                  </details>
                  <details className="faq-item">
                    <summary className="faq-q">Is patient data used to train the model?</summary>
                    <div className="faq-a">
                      <p>Never without explicit, revocable consent. Patient data is end-to-end encrypted from intake. Contribution to the training dataset is a separate, opt-in decision, it is not a condition of using the platform.</p>
                    </div>
                  </details>
                </div>
              </section>

              <section className="faq-group" id="for-clinicians">
                <h2 className="faq-group-title">For clinicians</h2>
                <div className="faq-list">
                  <details className="faq-item">
                    <summary className="faq-q">How do clinicians interact with the platform?</summary>
                    <div className="faq-a">
                      <p>Specialists receive structured cases, not raw inboxes. Each case surfaces the model-flagged findings alongside the original signal, with provenance and confidence on every claim. Clinicians can confirm findings, refine them, or disagree, and each decision is captured as structured supervision that feeds back into the next training cycle.</p>
                    </div>
                  </details>
                  <details className="faq-item">
                    <summary className="faq-q">Are clinicians compensated for their time?</summary>
                    <div className="faq-a">
                      <p>Expert annotations carry provenance metadata, specialty, agreement rate, and influence on model behaviour. Advisors who shape model behaviour at a structural level are credited by name in model documentation and any research publications. Compensation structures are being defined as the platform matures.</p>
                    </div>
                  </details>
                  <details className="faq-item">
                    <summary className="faq-q">What specialties are accepted into the expert network?</summary>
                    <div className="faq-a">
                      <p>The expert network is currently open to certified respiratory physicians, pulmonologists, radiologists with respiratory specialisation, and ENTs. Eligibility requirements and the onboarding process are detailed in the clinical access request form.</p>
                    </div>
                  </details>
                  <details className="faq-item">
                    <summary className="faq-q">How does clinician feedback improve the model?</summary>
                    <div className="faq-a">
                      <p>Every clinician decision, confirm, refine, or disagree, is captured as structured supervision. Disagreements are particularly valuable: they are the most precise training signal the system can receive, because they identify exactly where the model&apos;s biological characterisation diverged from clinical reality. This feedback feeds directly into the next training run.</p>
                    </div>
                  </details>
                </div>
              </section>

              <section className="faq-group" id="privacy">
                <h2 className="faq-group-title">Privacy & security</h2>
                <div className="faq-list">
                  <details className="faq-item">
                    <summary className="faq-q">What compliance standards does Senebiclabs meet?</summary>
                    <div className="faq-a">
                      <p>The platform is built toward HIPAA readiness, GDPR compliance, ISO 13485, and SOC 2 Type II. FDA pre-submission engagement is in progress. Specific compliance documentation is available under NDA for institutional partners evaluating the platform.</p>
                    </div>
                  </details>
                  <details className="faq-item">
                    <summary className="faq-q">How is patient data protected?</summary>
                    <div className="faq-a">
                      <p>Patient intake is end-to-end encrypted. Data is stored with access controls appropriate to health data at this sensitivity level. Patient records are never used for model training without explicit, revocable consent, and that consent can be withdrawn at any time without affecting access to care.</p>
                    </div>
                  </details>
                  <details className="faq-item">
                    <summary className="faq-q">Who has access to patient data?</summary>
                    <div className="faq-a">
                      <p>Patient data is accessible only to the clinician assigned to the case and to the patient themselves. It is not accessible to researchers, other clinicians, or the model training pipeline without the patient&apos;s explicit consent for each use.</p>
                    </div>
                  </details>
                </div>
              </section>

              <section className="faq-group" id="access">
                <h2 className="faq-group-title">Access & pricing</h2>
                <div className="faq-list">
                  <details className="faq-item">
                    <summary className="faq-q">How do I get access to the platform?</summary>
                    <div className="faq-a">
                      <p>Senebiclabs is in active development. We are preparing early access for research groups, pulmonology teams, and hospital systems. Use the request form on the main page to express interest, we will follow up directly.</p>
                    </div>
                  </details>
                  <details className="faq-item">
                    <summary className="faq-q">Is there a research API?</summary>
                    <div className="faq-a">
                      <p>Yes. The Senebiclabs detection engine is available to academic partners under a data-use agreement. Access is free for non-commercial publications. Reproducibility is built in, every finding is traceable to the source statistics. Contact us through the research API path on the main page.</p>
                    </div>
                  </details>
                  <details className="faq-item">
                    <summary className="faq-q">What does clinical access cost?</summary>
                    <div className="faq-a">
                      <p>Pricing for institutional clinical access is discussed as part of the onboarding process and depends on the scale of deployment and the type of integration required. Contact us to begin that conversation.</p>
                    </div>
                  </details>
                </div>
              </section>

            </div>
          </div>
        </div>
      </div>

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
                Senebiclabs
              </a>
              <p style={{ marginTop: "18px", maxWidth: "300px", lineHeight: "1.6", color: "var(--slate)", fontSize: "13.5px" }}>
                Biological intelligence connecting patients, clinicians,
                and the research community, starting with respiratory.
              </p>
            </div>
            <div>
              <h5>Platform</h5>
              <ul>
                <li><a href="/#patient">For Patients</a></li>
                <li><a href="/#clinic">For Clinicians</a></li>
                <li><a href="/#engine">Detection Engine</a></li>
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
            <span>© 2026 Senebiclabs Inc. · All rights reserved</span>
            <span>Built for the air we share.</span>
          </div>
        </div>
      </footer>
    </>
  );
}
