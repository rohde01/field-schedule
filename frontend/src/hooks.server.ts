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
            data: { user },
            error,
        } = await event.locals.supabase.auth.getUser()
        if (error) {
            return { session: null, user: null }
        }

        return { session, user }
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

    // Don't protect root, login, and register routes
    const isPublicRoute = event.url.pathname === '/' || 
        event.url.pathname.startsWith('/login') || 
        event.url.pathname.startsWith('/register')
        
    if (!event.locals.session && !isPublicRoute) {
        throw redirect(303, '/login')
    }

    if (event.locals.session && (event.url.pathname === '/login' || event.url.pathname === '/register')) {
        throw redirect(303, '/')
    }

    return resolve(event)
}

export const handle: Handle = sequence(supabase, authGuard)
