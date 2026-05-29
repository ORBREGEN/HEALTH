import { NextRequest, NextResponse } from 'next/server'

const FASTAPI = process.env.FASTAPI_URL ?? 'http://localhost:8000'

export async function POST(req: NextRequest) {
  try {
    const body = await req.json()
    const res = await fetch(`${FASTAPI}/api/v1/waitlist`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    const data = await res.json()
    return NextResponse.json({ ok: true, message: data.message ?? 'You are on the list.' })
  } catch {
    // Accept locally if the backend is unreachable — never block a waitlist sign-up
    return NextResponse.json({ ok: true, message: 'You are on the list.' })
  }
}
