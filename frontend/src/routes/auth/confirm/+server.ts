import { redirect } from '@sveltejs/kit'
import { type EmailOtpType } from '@supabase/supabase-js'
import type { RequestHandler } from './$types'

export const GET: RequestHandler = async ({ url, locals: { supabase } }) => {
  const token_hash = url.searchParams.get('token_hash') as string
  const type = url.searchParams.get('type') as EmailOtpType | null
  const next = url.searchParams.get('next') ?? '/'


  // Create base URL and ensure 'next' is treated as a path
  const redirectTo = new URL(url.origin)
  redirectTo.pathname = next.startsWith('http') ? new URL(next).pathname : next
  redirectTo.searchParams.delete('token_hash')
  redirectTo.searchParams.delete('type')

  if (token_hash && type) {
    const { error } = await supabase.auth.verifyOtp({ token_hash, type })
    if (!error) {
      // Redirect to settings page after successful validation
      redirectTo.pathname = '/settings'
      throw redirect(303, redirectTo.pathname)
    }
  }

  redirectTo.pathname = '/auth/error'
  throw redirect(303, redirectTo.pathname)
}