import { NextRequest, NextResponse } from 'next/server'

const FASTAPI = process.env.FASTAPI_URL ?? 'http://localhost:8000'

export const maxDuration = 300

export async function POST(req: NextRequest) {
  try {
    // Pipe req.body directly to FastAPI — no buffering in Node.js RAM.
    // req.formData() would load the entire file into memory; passing req.body streams it.
    const contentType = req.headers.get('content-type') ?? ''
    const contentLength = req.headers.get('content-length') ?? ''

    const headers: Record<string, string> = { 'content-type': contentType }
    if (contentLength) headers['content-length'] = contentLength

    const res = await fetch(`${FASTAPI}/api/v1/analyse/upload`, {
      method: 'POST',
      headers,
      body: req.body,
      // Required for streaming request bodies in Node.js fetch
      // @ts-ignore
      duplex: 'half',
    })

    const data = await res.json()
    return NextResponse.json(data, { status: res.status })
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error'
    return NextResponse.json(
      { detail: `Backend unreachable or file processing failed: ${message}` },
      { status: 503 },
    )
  }
}
