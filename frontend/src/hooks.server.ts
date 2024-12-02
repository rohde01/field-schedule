import { validateUser } from '$lib/server/auth';
import type { Handle } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
    const token = event.cookies.get('token');
    event.locals.user = token ? await validateUser(token) : null;

    const protectedRoutes = ['/dashboard'];
    const isProtectedRoute = protectedRoutes.some(route => 
        event.url.pathname.startsWith(route)
    );

    if (isProtectedRoute && !event.locals.user) {
        return new Response('Redirect', {
            status: 303,
            headers: { Location: '/login' }
        });
    }

    return resolve(event);
};