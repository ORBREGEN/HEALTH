import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const COOKIE = 'analyse_access'

export function middleware(request: NextRequest) {
  const token = request.cookies.get(COOKIE)?.value
  const valid = process.env.ANALYSE_ACCESS_TOKEN

  if (!valid) return NextResponse.next() // no token set in env → open in dev

  if (token === valid) return NextResponse.next()

  const requestPage = new URL('/analyse/request', request.url)
  return NextResponse.redirect(requestPage)
}

export const config = {
  matcher: ['/analyse'],
}
