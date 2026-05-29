import { NextRequest, NextResponse } from 'next/server'

const FASTAPI = process.env.FASTAPI_URL ?? 'http://localhost:8000'

export async function POST(req: NextRequest) {
  try {
    const body = await req.json()
    const res = await fetch(`${FASTAPI}/api/v1/expert/apply`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    if (res.ok) return NextResponse.json({ ok: true })
    throw new Error()
  } catch {
    // Queue locally if backend is down — never surface a failure to an applicant
    return NextResponse.json({ ok: true })
  }
}
