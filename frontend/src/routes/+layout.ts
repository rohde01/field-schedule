import { createBrowserClient, createServerClient, isBrowser } from '@supabase/ssr'
import { PUBLIC_SUPABASE_ANON_KEY, PUBLIC_SUPABASE_URL } from '$env/static/public'
import type { LayoutLoad } from './$types'
import type { User as CustomUser } from '$lib/schemas/user'

export const load: LayoutLoad = async (event) => {
  // Declare a dependency so the layout can be invalidated, for example, on
  // session refresh.
  event.depends('supabase:auth')

  const supabase = isBrowser()
    ? createBrowserClient(PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_ANON_KEY, {
        global: {
          fetch: event.fetch,
        },
      })
    : createServerClient(PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_ANON_KEY, {
        global: {
          fetch: event.fetch,
        },
        cookies: {
          getAll() {
            return event.data.cookies
          },
        },
      })

  // It's fine to use `getSession` here, because on the client, `getSession` is
  // safe, and on the server, it reads `session` from the `LayoutData`, which
  // safely checked the session using `safeGetSession`.
  const {
    data: { session },
  } = await supabase.auth.getSession()

  const {
    data: { user: supaUser },
  } = await supabase.auth.getUser()
  const user: CustomUser | null = supaUser ? (supaUser as CustomUser) : null

  return { 
    session, 
    supabase, 
    user,
    cookies: {},
    teams: event.data.teams || [],
    facilities: event.data.facilities || [],
    fields: event.data.fields || [],
    schedules: event.data.schedules || []
  }
}