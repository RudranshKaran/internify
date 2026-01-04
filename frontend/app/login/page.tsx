'use client'

import { useState, useEffect, useRef } from 'react'
import { supabase } from '@/lib/supabaseClient'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Mail, Lock, Loader2 } from 'lucide-react'
import { toast } from '@/components/Toast'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLogin, setIsLogin] = useState(true)
  const [loading, setLoading] = useState(false)
  const [checking, setChecking] = useState(true)
  const router = useRouter()
  const hasCheckedAuth = useRef(false)
  const isRedirecting = useRef(false)
  const isLoggingIn = useRef(false)

  useEffect(() => {
    // Check if already logged in - only once on mount
    if (hasCheckedAuth.current || isLoggingIn.current) return
    hasCheckedAuth.current = true
    
    const checkSession = async () => {
      try {
        // Add a timeout to prevent infinite loading
        const timeoutPromise = new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Session check timeout')), 3000)
        )
        
        const sessionPromise = supabase.auth.getSession()
        
        const { data: { session } } = await Promise.race([sessionPromise, timeoutPromise]) as any
        console.log('Login page: Initial check, session:', session ? 'exists' : 'none')
        
        if (session && !isRedirecting.current && !isLoggingIn.current) {
          console.log('Login page: User already logged in, redirecting to dashboard')
          isRedirecting.current = true
          // User is already logged in, redirect to dashboard
          window.location.replace('/dashboard')
        } else {
          setChecking(false)
        }
      } catch (error) {
        console.error('Login page: Auth check error:', error)
        // Always set checking to false so the page can be used
        setChecking(false)
      }
    }
    
    checkSession()
  }, [router])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Prevent double submission or submission during redirect
    if (loading || isRedirecting.current || isLoggingIn.current) return
    
    isLoggingIn.current = true
    setLoading(true)

    try {
      if (isLogin) {
        console.log('Login page: Attempting login with email:', email)
        const { data, error } = await supabase.auth.signInWithPassword({
          email,
          password,
        })
        
        if (error) {
          console.error('Login page: Login error:', error.message, error)
          isLoggingIn.current = false
          throw error
        }
        
        console.log('Login page: Login successful!', {
          hasSession: !!data.session,
          hasUser: !!data.user,
          userId: data.user?.id,
          userEmail: data.user?.email
        })
        
        if (data.session) {
          isRedirecting.current = true
          toast.success('Logged in successfully!')
          console.log('Login page: Session established, verifying persistence...')
          
          // Wait for session to be persisted and verify it's retrievable
          // This prevents race conditions on the dashboard
          let attempts = 0
          const maxAttempts = 10
          while (attempts < maxAttempts) {
            await new Promise(resolve => setTimeout(resolve, 100))
            const { data: { session: verifiedSession } } = await supabase.auth.getSession()
            if (verifiedSession) {
              console.log('Login page: Session verified in storage, redirecting...')
              window.location.href = '/dashboard'
              return
            }
            attempts++
          }
          
          // If we couldn't verify, redirect anyway
          console.log('Login page: Timeout waiting for session persistence, redirecting anyway...')
          window.location.href = '/dashboard'
          return // Don't reset loading
        }
      } else {
        const { data, error } = await supabase.auth.signUp({
          email,
          password,
        })
        
        if (error) throw error
        
        if (data.user) {
          if (data.session) {
            isRedirecting.current = true
            toast.success('Account created! Redirecting...')
            setTimeout(() => {
              window.location.href = '/dashboard'
            }, 500)
            return // Don't reset loading
          } else {
            toast.success('Account created! Please check your email for verification.')
            setLoading(false)
          }
        }
      }
    } catch (error: any) {
      console.error('Auth error:', error)
      const errorMessage = error.message || error.error_description || 'An error occurred'
      toast.error(errorMessage)
      setLoading(false)
      isLoggingIn.current = false
    } finally {
      // Reset loading if not redirecting
      if (!isRedirecting.current) {
        setLoading(false)
        isLoggingIn.current = false
      }
    }
  }

  // Show loading while checking session
  if (checking) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-purple-50">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-purple-50 px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {isLogin ? 'Welcome Back' : 'Create Account'}
          </h1>
          <p className="text-gray-600">
            {isLogin ? 'Sign in to your account' : 'Start your internship journey'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email Address
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                placeholder="you@example.com"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                placeholder="••••••••"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {loading ? (
              <>
                <Loader2 className="animate-spin w-5 h-5 mr-2" />
                Please wait...
              </>
            ) : (
              isLogin ? 'Sign In' : 'Create Account'
            )}
          </button>
        </form>

        <div className="mt-6 text-center">
          <button
            onClick={() => {
              if (!loading) {
                setIsLogin(!isLogin)
                setEmail('')
                setPassword('')
              }
            }}
            disabled={loading}
            className="text-primary hover:text-primary/80 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLogin ? "Don't have an account? Sign Up" : 'Already have an account? Sign In'}
          </button>
        </div>

        <div className="mt-6 text-center">
          <Link href="/" className="text-gray-600 hover:text-gray-900 text-sm">
            ← Back to Home
          </Link>
        </div>
      </div>
    </div>
  )
}
