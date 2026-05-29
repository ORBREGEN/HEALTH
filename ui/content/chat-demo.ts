export interface ChatMessage {
  role: 'user' | 'ai'
  tag?: string
  text: string
}

export const TRIAGE_CONVERSATION: ChatMessage[] = [
  {
    role: 'user',
    text: 'My grandfather has been coughing at night for 3 weeks. There’s a wheeze sometimes. He’s 68.',
  },
  {
    role: 'ai',
    tag: 'Triage · L01',
    text: 'Thank you. A few quick questions: is the cough dry or producing phlegm? Has he had a fever, or any chest tightness when climbing stairs?',
  },
  {
    role: 'user',
    text: 'Some phlegm in the morning. No fever. Yes — gets short of breath on stairs.',
  },
  {
    role: 'ai',
    tag: 'Match · L03',
    text: 'Based on what you’ve described, a pulmonologist is the right starting point. I’ve identified three specialists nearby with availability today.',
  },
]
