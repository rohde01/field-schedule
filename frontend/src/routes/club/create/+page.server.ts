import type { PageServerLoad, Actions } from './$types'; 
import { fail, redirect } from '@sveltejs/kit';
import { API_URL } from '$env/static/private';

export const load = (async ({ locals }) => {
    return {};
}) satisfies PageServerLoad;

export const actions: Actions = {
    default: async ({ request, locals, fetch }) => {
        if (!locals.user) {
            return fail(401, { error: 'Unauthorized' });
        }

        const data = await request.formData();
        const name = data.get('name')?.toString();

        if (!name) {
            return fail(400, { error: 'Club name is required' });
        }

        const response = await fetch(`${API_URL}/clubs/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${locals.token}`
            },
            body: JSON.stringify({
                name: name
            })
        });

        if (!response.ok) {
            return fail(400, { error: 'Failed to create club' });
        }

        const clubData = await response.json();
        
        if (locals.user) {
            locals.user.primary_club_id = clubData.club_id;
        }
        
        return { success: true };
    }
};