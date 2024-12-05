import type { PageServerLoad, Actions } from './$types';
import { error, fail } from '@sveltejs/kit';

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

export const actions = {
    create: async ({ request, locals, fetch }) => {
        if (!locals.user) {
            return fail(401, { error: 'User not authenticated' });
        }

        const data = await request.formData();
        const name = data.get('name')?.toString();
        const is_primary = data.get('is_primary') === 'true';

        if (!name) {
            return fail(400, { error: 'Facility name is required' });
        }

        const response = await fetch('http://localhost:8000/facilities', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                club_id: locals.user.primary_club_id,
                name,
                is_primary
            })
        });

        if (!response.ok) {
            return fail(response.status, { error: 'Failed to create facility' });
        }

        const facility = await response.json();
        return { facility };
    }
} satisfies Actions;