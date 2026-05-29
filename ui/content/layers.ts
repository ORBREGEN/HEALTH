export type LayerStatus = 'public' | 'core' | 'expert' | 'future'

export interface LayerDef {
  id: string
  label: string
  badge: string
  status: LayerStatus
  heading: string
  desc: string
  bullets: string[]
}

export const LAYERS: LayerDef[] = [
  {
    id: 'L01',
    label: 'L · 01 / Public',
    badge: 'Patient intake',
    status: 'public',
    heading: 'Patients reach the right specialist',
    desc: 'Anyone with respiratory symptoms reaches the right specialist. No referral required. No medical vocabulary needed. The platform meets patients where they are, any language, any connection, and matches them based on what their biology suggests, not how they describe it.',
    bullets: [
      'Reaches anyone, in any language',
      'Works on any connection, 2G, basic phone, no app required',
      'Matched by biological pattern, not referral history',
    ],
  },
  {
    id: 'L02',
    label: 'L · 02 / Core',
    badge: 'Detection engine',
    status: 'core',
    heading: 'Every case arrives with the picture already drawn',
    desc: 'The specialist sees what is out of range before they open the file. Which cells. Which signals. What deviates from a reference built from 2.28 million healthy human lung cells. The engine describes. The physician decides.',
    bullets: [
      'What is out of range, surfaced, ranked, fully traceable',
      'Every finding links back to its source, nothing opaque',
      'Open to researchers through a documented API',
    ],
  },
  {
    id: 'L03',
    label: 'L · 03 / Expert',
    badge: 'Expert network',
    status: 'expert',
    heading: 'Clinical judgment shapes what comes next',
    desc: 'Physicians review structured findings, not noise. Their decisions, confirm, refine, disagree, feed directly back into the model. Every correction improves the next case. Expert judgment does not just help one patient, it improves outcomes for every patient the platform will ever see.',
    bullets: [
      'Structured findings with full provenance, nothing the physician cannot verify',
      'Every decision improves what the next specialist sees',
      'Contributions credited by name in model documentation and publications',
    ],
  },
  {
    id: 'L04',
    label: 'L · 04 / Future',
    badge: 'In development',
    status: 'future',
    heading: 'Treatment will follow understanding',
    desc: 'When the platform knows precisely what deviated and how, it can reason about reversal. Treatment grounded in biological mechanism, not generic protocol. Drug design directions for novel mechanisms. This is the destination. It is where the platform is going.',
    bullets: [
      'Treatment grounded in what actually deviated, not what typically presents',
      'Interventions targeted at the specific disrupted pathway',
      'Drug design directions when no existing treatment fits the mechanism',
    ],
  },
]
