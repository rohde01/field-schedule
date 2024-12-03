import { validateUser } from '$lib/server/auth';
import { routeConfig } from '$lib/server/routeConfig';
import type { Handle } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
    const token = event.cookies.get('token');
    event.locals.user = token ? await validateUser(token) : null;

    const path = event.url.pathname;
    const routeMeta = Object.hasOwn(routeConfig, path) ? routeConfig[path as keyof typeof routeConfig] : undefined;

    if (routeMeta?.requiresAuth && !event.locals.user) {
        return new Response('Redirect', {
            status: 303,
            headers: { Location: '/login' },
        });
    }

    if (routeMeta?.requiresClub && !event.locals.user?.primary_club_id) {
        return new Response('Redirect', {
            status: 303,
            headers: { Location: '/club/create' },
        });
    }

    return resolve(event);
};
