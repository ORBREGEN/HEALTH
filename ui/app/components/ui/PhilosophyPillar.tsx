import type { Pillar } from '@/content/philosophy'

interface Props {
  pillar: Pillar
}

export default function PhilosophyPillar({ pillar }: Props) {
  return (
    <div className="pillar">
      <span className="pn">{pillar.number}</span>
      <h3>{pillar.heading}</h3>
      <p>{pillar.body}</p>
    </div>
  )
}
