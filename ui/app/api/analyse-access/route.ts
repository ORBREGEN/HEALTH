import { NextRequest, NextResponse } from 'next/server'

export async function POST(req: NextRequest) {
  const { code } = await req.json()
  const valid = process.env.ANALYSE_ACCESS_TOKEN

  if (!valid || code !== valid) {
    return NextResponse.json({ error: 'Invalid access code.' }, { status: 401 })
  }

  const res = NextResponse.json({ ok: true })
  res.cookies.set('analyse_access', valid, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    path: '/',
    maxAge: 60 * 60 * 24 * 90, // 90 days
  })
  return res
}
