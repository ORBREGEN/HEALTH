import { NextResponse } from 'next/server'

const FASTAPI = process.env.FASTAPI_URL ?? 'http://localhost:8000'

export async function GET() {
  try {
    const res = await fetch(`${FASTAPI}/api/v1/model/status`, {
      next: { revalidate: 30 },
    })
    const data = await res.json()
    return NextResponse.json(data, { status: res.status })
  } catch {
    return NextResponse.json(
      { is_ready: false, message: 'Backend unreachable' },
      { status: 503 },
    )
  }
}
