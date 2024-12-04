import type { PageServerLoad, Actions } from './$types'; 
import { fail, redirect } from '@sveltejs/kit';

export const load = (async ({ locals }) => {
    return {};
}) satisfies PageServerLoad;

export const actions: Actions = {
    default: async ({ request, locals }) => {
        if (!locals.user) {
            return fail(401, { error: 'Unauthorized' });
        }

        const data = await request.formData();
        const name = data.get('name')?.toString();

        if (!name) {
            return fail(400, { error: 'Club name is required' });
        }

        const response = await fetch('http://localhost:8000/clubs/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name,
                user_id: parseInt(locals.user.id)
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