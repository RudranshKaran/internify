import { NextRequest, NextResponse } from 'next/server'

/**
 * Auth callback route — handles redirects from Supabase email confirmation,
 * password reset, and magic link flows.
 *
 * Supabase appends ?code=...&... to the redirect URL; the code is picked up
 * client-side by supabase-js via onAuthStateChange / getSession.
 */
export async function GET(request: NextRequest) {
  const requestUrl = new URL(request.url)
  const code = requestUrl.searchParams.get('code')

  if (code) {
    // Return a page that exchanges the code for a session via the browser.
    return new Response(
      `<!doctype html>
<html>
<head><title>Redirecting…</title></head>
<body>
<script>
  ;(async function () {
    const { createClient } = await import('@supabase/supabase-js')
    const supabase = createClient(
      '${process.env.NEXT_PUBLIC_SUPABASE_URL}' ,
      '${process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY}',
      { auth: { persistSession: true, autoRefreshToken: true } }
    )
    await supabase.auth.exchangeCodeForSession('${code}')
    window.location.href = '/dashboard'
  })()
</script>
<p>Completing sign-in…</p>
</body>
</html>`,
      {
        headers: { 'content-type': 'text/html;charset=utf-8' },
      },
    )
  }

  // No code — just forward to dashboard
  return NextResponse.redirect(new URL('/dashboard', requestUrl))
}
