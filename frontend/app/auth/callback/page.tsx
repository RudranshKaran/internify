'use client'

import { useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabaseClient'
import { Loader2 } from 'lucide-react'

export default function AuthCallbackPage() {
  const router = useRouter()
  const exchanged = useRef(false)

  useEffect(() => {
    if (exchanged.current) return
    exchanged.current = true

    const exchangeCode = async () => {
      const { data, error } = await supabase.auth.exchangeCodeForSession(
        window.location.search
      )

      if (error) {
        console.error('[AUTH/CALLBACK] Code exchange failed:', error.message)
        router.push('/login')
        return
      }

      if (data.session) {
        router.push('/dashboard')
      }
    }

    exchangeCode()
  }, [router])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-purple-50">
      <div className="text-center space-y-4">
        <Loader2 className="w-8 h-8 animate-spin text-primary mx-auto" />
        <p className="text-gray-600">Completing sign-in…</p>
      </div>
    </div>
  )
}
