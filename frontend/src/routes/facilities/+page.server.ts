import type { PageServerLoad } from './$types';
import { error } from '@sveltejs/kit';

export const load = (async ({ locals, fetch }) => {
    if (!locals.user) {
        throw error(401, 'User not authenticated');
    }

    const response = await fetch(`http://localhost:8000/facilities/club/${locals.user.primary_club_id}`);
    
    if (!response.ok) {
        throw error(response.status, 'Failed to fetch facilities');
    }

    const facilities = await response.json();
    return { facilities };
}) satisfies PageServerLoad;