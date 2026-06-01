'use client'
import { useEffect, useState } from 'react'

interface ToastProps {
  message: string
  onDismiss: () => void
}

export default function Toast({ message, onDismiss }: ToastProps) {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const show = requestAnimationFrame(() => setVisible(true))
    const hide = setTimeout(() => {
      setVisible(false)
      setTimeout(onDismiss, 300)
    }, 5000)
    return () => { cancelAnimationFrame(show); clearTimeout(hide) }
  }, [onDismiss])

  return (
    <div
      onClick={() => { setVisible(false); setTimeout(onDismiss, 300) }}
      style={{
        position: 'fixed',
        bottom: 32,
        left: '50%',
        transform: `translateX(-50%) translateY(${visible ? 0 : 16}px)`,
        opacity: visible ? 1 : 0,
        transition: 'opacity 0.25s ease, transform 0.25s ease',
        background: '#1a1a1a',
        border: '1px solid rgba(255,255,255,0.12)',
        borderRadius: 10,
        padding: '13px 20px',
        display: 'flex',
        alignItems: 'center',
        gap: 12,
        cursor: 'pointer',
        zIndex: 9999,
        maxWidth: 'calc(100vw - 48px)',
        boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
      }}
    >
      <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#ef4444', flexShrink: 0 }} />
      <span style={{ fontFamily: 'Geist Mono, monospace', fontSize: 12, letterSpacing: '0.06em', color: '#fff', lineHeight: 1.5 }}>
        {message}
      </span>
    </div>
  )
}
