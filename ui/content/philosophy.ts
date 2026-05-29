export interface Pillar {
  number: string
  heading: string
  body: string
}

export const PHILOSOPHY_PILLARS: Pillar[] = [
  {
    number: '01',
    heading: 'The model must learn from life, not from rules',
    body: 'Biology is too complex for manually curated signatures. Every reference in Senebiclabs comes from real human cells, 2.28 million of them across donors, tissues, and conditions. The statistics are computed from the data, not assumed by a researcher.',
  },
  {
    number: '02',
    heading: 'Description comes before diagnosis',
    body: 'The system characterises what it observes: which cell populations are shifted, which genes deviate, which processes are dysregulated. It does not reach for a disease name. That reasoning belongs to a clinician with full context, not an algorithm with a lookup table.',
  },
  {
    number: '03',
    heading: 'Access is not a feature, it is the mission',
    body: 'The same intelligence that serves a research lab should be reachable by anyone, anywhere in the world. If the platform is only useful to the well-resourced, it has not solved the problem, it has redecorated it.',
  },
  {
    number: '04',
    heading: 'Disagreement is the most valuable signal',
    body: 'When a clinician corrects the model, that correction is not a failure, it is the most precise training data the system can receive. The flywheel runs on expert disagreement captured at scale. That disagreement is credited and attributed, because it is worth more than agreement.',
  },
  {
    number: '05',
    heading: 'Treatment follows understanding',
    body: 'You cannot know how to correct something until you know precisely what deviated and why. The path to treatment intelligence runs through biological clarity, not through naming conditions, but through characterising their mechanisms with enough precision to reverse them.',
  },
]
