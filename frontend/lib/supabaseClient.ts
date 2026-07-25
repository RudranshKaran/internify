import { createClient, type SupabaseClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL?.trim()
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY?.trim()

const createMissingClient = (): SupabaseClient => {
  const missingError = new Error(
    'Missing Supabase environment variables. Set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY in frontend/.env.local.'
  )

  const notConfigured = async () => ({
    data: { session: null, user: null },
    error: missingError,
  })

  const auth = {
    getSession: notConfigured,
    getUser: notConfigured,
    signOut: async () => ({ error: missingError }),
    onAuthStateChange: () => ({
      data: {
        subscription: {
          unsubscribe: () => undefined,
        },
      },
    }),
  }

  const storage = {
    from: () => ({
      upload: async () => {
        throw missingError
      },
      getPublicUrl: () => ({ data: { publicUrl: '' } }),
      remove: async () => {
        throw missingError
      },
    }),
  }

  const from = () => ({
    select: () => ({
      eq: () => ({
        eq: () => ({
          order: () => ({
            limit: () => ({
              execute: async () => {
                throw missingError
              },
            }),
          }),
        }),
      }),
    }),
    insert: () => ({
      execute: async () => {
        throw missingError
      },
    }),
    delete: () => ({
      eq: () => ({
        eq: () => ({
          execute: async () => {
            throw missingError
          },
        }),
      }),
    }),
  })

  return {
    auth,
    storage,
    from,
  } as unknown as SupabaseClient
}

const siteUrl = (process.env.NEXT_PUBLIC_SITE_URL || '').replace(/\/+$/, '')

export const supabase: SupabaseClient =
  supabaseUrl && supabaseAnonKey
    ? createClient(supabaseUrl, supabaseAnonKey, {
        auth: {
          persistSession: true,
          autoRefreshToken: true,
        },
      })
    : createMissingClient()

/** Resolve the redirect URL for auth flows (email confirmations, etc.).
 *  Uses the configured site URL in production, falls back to window origin in dev. */
export function getAuthRedirectUrl(): string {
  if (siteUrl) return siteUrl
  if (typeof window !== 'undefined') return window.location.origin
  return 'http://localhost:3000'
}

// Helper function to get current user
export const getCurrentUser = async () => {
  const { data: { user }, error } = await supabase.auth.getUser()
  return { user, error }
}

// Helper function to get session
export const getSession = async () => {
  const { data: { session }, error } = await supabase.auth.getSession()
  return { session, error }
}

// Helper function to sign out
export const signOut = async () => {
  // Clear localStorage to prevent data leakage between users
  localStorage.removeItem('selectedInternship')
  
  const { error } = await supabase.auth.signOut()
  return { error }
}
