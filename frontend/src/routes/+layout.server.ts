import type { LayoutServerLoad } from './$types';
import { error } from '@sveltejs/kit';
import type { Facility } from '$lib/schemas/facility';
import type { Field } from '$lib/schemas/field';
import type { Team } from '$lib/schemas/team';
import type { Constraint } from '$lib/schemas/schedule';

export const load: LayoutServerLoad = async ({ locals, fetch }) => {

    if (!locals.user?.primary_club_id) {
        console.log('No primary_club_id found');
        return {
            facilities: [],
            fields: [],
            constraints: []
        };
    }

    try {
        const [facilitiesResponse, fieldsResponse, teamsResponse, constraintsResponse] = await Promise.all([
            fetch(`http://localhost:8000/facilities/club/${locals.user.primary_club_id}`, {
                headers: {
                    'Authorization': `Bearer ${locals.token}`
                }
            }),
            fetch(`http://localhost:8000/fields/club/${locals.user.primary_club_id}`, {
                headers: {
                    'Authorization': `Bearer ${locals.token}`
                }
            }),
            fetch(`http://localhost:8000/teams?club_id=${locals.user.primary_club_id}`, {
                headers: {
                    'Authorization': `Bearer ${locals.token}`
                }
            }), 
            fetch(`http://localhost:8000/schedules/${locals.user.primary_club_id}/constraints`, {
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

        if (!teamsResponse.ok) {
            console.error('Failed to fetch teams:', teamsResponse.status, await teamsResponse.text());
            throw error(teamsResponse.status, 'Failed to fetch teams');
        }

        if (!constraintsResponse.ok) {
            console.error('Failed to fetch constraints:', constraintsResponse.status, await constraintsResponse.text());
            throw error(constraintsResponse.status, 'Failed to fetch constraints');
        }

        const facilities: Facility[] = await facilitiesResponse.json();
        const fields: Field[] = await fieldsResponse.json();
        const teams: Team[] = await teamsResponse.json();
        const constraints: Constraint[] = await constraintsResponse.json();
        
        console.log('Fetched facilities:', facilities);
        console.log('Fetched fields:', fields);
        console.log('Fetched teams:', teams);

        return {
            facilities,
            fields,
            teams,
            constraints,
            user: locals.user
        };
    } catch (err) {
        console.error('Error in layout load function:', err);
        throw error(500, 'Internal Server Error');
    }
};
