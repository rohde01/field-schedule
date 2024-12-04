import type { PageServerLoad } from './$types';

export const load = (async ({ locals }) => {
    return {
        firstName: locals.user?.firstName || 'Guest'
    };
}) satisfies PageServerLoad;