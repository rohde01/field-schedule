import type { LayoutServerLoad } from './$types';

import { error } from '@sveltejs/kit';
import type { Facility } from '$lib/schemas/facility';
import type { Field } from '$lib/schemas/field';

export const load: LayoutServerLoad = async ({ locals, fetch }) => {

    if (!locals.user?.primary_club_id) {
        console.log('No primary_club_id found');
        return {
            facilities: [],
            fields: []
        };
    }

    try {
        const [facilitiesResponse, fieldsResponse] = await Promise.all([
            fetch(`http://localhost:8000/facilities/club/${locals.user.primary_club_id}`, {
                headers: {
                    'Authorization': `Bearer ${locals.token}`
                }
            }),
            fetch(`http://localhost:8000/fields/club/${locals.user.primary_club_id}`, {
                headers: {
                    'Authorization': `Bearer ${locals.token}`
                }
            })
        ]);

        if (!facilitiesResponse.ok) {
            const errorText = await facilitiesResponse.text();
            console.error('Failed to fetch facilities:', facilitiesResponse.status, errorText);
            throw error(facilitiesResponse.status, 'Failed to fetch facilities');
        }

        if (!fieldsResponse.ok) {
            const errorText = await fieldsResponse.text();
            console.error('Failed to fetch fields:', fieldsResponse.status, errorText);
            throw error(fieldsResponse.status, 'Failed to fetch fields');
        }

        const facilities: Facility[] = await facilitiesResponse.json();
        const fields: Field[] = await fieldsResponse.json();
        
        console.log('Fetched facilities:', facilities);
        console.log('Fetched fields:', fields);

        return {
            facilities,
            fields,
            user: locals.user
        };
    } catch (err) {
        console.error('Error in load function:', err);
        throw error(500, 'Internal Server Error');
    }
};
