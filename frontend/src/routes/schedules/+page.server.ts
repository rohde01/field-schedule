import type { PageServerLoad } from './$types';
import { error } from '@sveltejs/kit';
import type { Schedule } from '$lib/schemas/schedule';

export const load = (async ({ fetch, locals }) => {
    if (!locals.user) {
        throw error(401, 'Unauthorized');
    }

    try {
        const response = await fetch(`http://localhost:8000/schedules/${locals.user.primary_club_id}/schedules`, {
            headers: {
                'Authorization': `Bearer ${locals.token}`
            }
        });
        if (!response.ok) throw new Error('Failed to fetch schedules');
        const schedules: Schedule[] = await response.json();
        
        return {
            schedules
        };
    } catch (e) {
        throw error(500, 'Error loading schedules');
    }
}) satisfies PageServerLoad;