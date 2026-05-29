export type ComplianceStatus = 'achieved' | 'in-progress' | 'planned'

export interface ComplianceItem {
  label: string
  status: ComplianceStatus
  display: string
}

export const COMPLIANCE_ITEMS: ComplianceItem[] = [
  { label: 'HIPAA',     status: 'in-progress', display: 'HIPAA · in progress' },
  { label: 'GDPR',      status: 'in-progress', display: 'GDPR · in progress' },
  { label: 'ISO 13485', status: 'planned',      display: 'ISO 13485 · planned' },
  { label: 'SOC 2',     status: 'planned',      display: 'SOC 2 · planned' },
  { label: 'FDA',       status: 'planned',      display: 'FDA · pre-submission planned' },
]
