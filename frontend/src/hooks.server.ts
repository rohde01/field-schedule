import { createServerClient } from '@supabase/ssr'
import { type Handle, redirect } from '@sveltejs/kit'
import { sequence } from '@sveltejs/kit/hooks'
import { PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_ANON_KEY } from '$env/static/public'

const supabase: Handle = async ({ event, resolve }) => {
    event.locals.supabase = createServerClient(PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_ANON_KEY, {
        cookies: {
            getAll: () => event.cookies.getAll(),
            setAll: (cookiesToSet) => {
                cookiesToSet.forEach(({ name, value, options }) => {
                    event.cookies.set(name, value, { ...options, path: '/' })
                })
            },
        },
    })

    event.locals.safeGetSession = async () => {
        const {
            data: { session },
        } = await event.locals.supabase.auth.getSession()
        if (!session) {
            return { session: null, user: null }
        }

        const {
            data: { user: authUser },
            error,
        } = await event.locals.supabase.auth.getUser()
        if (error || !authUser) {
            return { session: null, user: null }
        }

        // Fetch full user data from users table
        const { data: userData } = await event.locals.supabase
            .from('users')
            .select('*')
            .eq('user_id', authUser.id)
            .single()

        return { session, user: userData }
    }

    return resolve(event, {
        filterSerializedResponseHeaders(name) {
            return name === 'content-range' || name === 'x-supabase-api-version'
        },
    })
}

const authGuard: Handle = async ({ event, resolve }) => {
    const { session, user } = await event.locals.safeGetSession()
    event.locals.session = session
    event.locals.user = user

    // If user is logged in and trying to access auth page, redirect to schedules
    if (session && event.url.pathname === '/auth') {
        throw redirect(303, '/schedules')
    }

    const isProtected = event.route.id?.startsWith('/(dashboard)')
    if (!isProtected) {
        return resolve(event)
    }

    if (!session) {
        throw redirect(303, '/auth')
    }

    // Redirect to onboarding if name or club is missing
    if (!event.url.pathname.startsWith('/settings') && (!user?.first_name || !user?.last_name || !user?.club_id)) {
        throw redirect(303, '/settings')
    }

    return resolve(event)
}

export const handle: Handle = sequence(supabase, authGuard)
