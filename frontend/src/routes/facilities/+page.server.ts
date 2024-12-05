import type { PageServerLoad, Actions } from './$types';
import { error, fail } from '@sveltejs/kit';

export const load = (async ({ locals, fetch }) => {
    if (!locals.user) {
        throw error(401, 'User not authenticated');
    }

    const facilitiesResponse = await fetch(`http://localhost:8000/facilities/club/${locals.user.primary_club_id}`);
    
    if (!facilitiesResponse.ok) {
        throw error(facilitiesResponse.status, 'Failed to fetch facilities');
    }

    const facilities = await facilitiesResponse.json();
    let fields = [];
    
    if (locals.facilityStatus?.selectedFacility) {
        const fieldsResponse = await fetch(`http://localhost:8000/fields/facility/${locals.facilityStatus.selectedFacility.facility_id}`);
        if (fieldsResponse.ok) {
            fields = await fieldsResponse.json();
        }
    }

    return { facilities, fields };
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

        try {
            const response = await fetch('http://localhost:8000/facilities', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name,
                    is_primary,
                    club_id: locals.user.primary_club_id
                })
            });

            if (!response.ok) {
                return fail(response.status, { error: 'Failed to create facility' });
            }

            const facility = await response.json();
            return { facility };
        } catch (error) {
            return fail(500, { error: 'Failed to create facility' });
        }
    }
} satisfies Actions;