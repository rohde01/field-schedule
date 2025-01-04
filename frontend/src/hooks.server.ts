import { validateAndRefreshTokens } from '$lib/server/auth';
import { routeConfig } from '$lib/server/routeConfig';
import type { Handle } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
    const token = event.cookies.get('token');
    const refreshToken = event.cookies.get('refresh_token');
    
    let user = null;
    if (token) {
        const { user: validatedUser, tokenRefreshed } = await validateAndRefreshTokens(
            token,
            refreshToken,
            event.cookies
        );
        user = validatedUser;
        
        if (tokenRefreshed) {
            const newToken = event.cookies.get('token') ?? null;
            event.locals.token = newToken;
        }
    }

    event.locals.token = token ?? null;
    event.locals.user = user;

    const path = event.url.pathname;
    const routeMeta = Object.hasOwn(routeConfig, path) ? routeConfig[path as keyof typeof routeConfig] : undefined;

    if (routeMeta?.requiresAuth && !event.locals.user) {
        // Clear cookies if authentication failed
        event.cookies.delete('token', { path: '/' });
        event.cookies.delete('refresh_token', { path: '/' });
        
        return new Response('Redirect', {
            status: 303,
            headers: { Location: '/login' },
        });
    }

    if (routeMeta?.requiresClub && !event.locals.user?.primary_club_id) {
        if (path !== '/club/create') {
            return new Response('Redirect', {
                status: 303,
                headers: { Location: '/club/create' },
            });
        }
    }

    return resolve(event);
};
