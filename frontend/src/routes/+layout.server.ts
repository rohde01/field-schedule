import type { LayoutServerLoad } from './$types';
import { error } from '@sveltejs/kit';
import type { Facility } from '$lib/schemas/facility';
import type { Field } from '$lib/schemas/field';
import type { Schedule } from '$lib/schemas/schedule';
import type { EventSchedule } from '$lib/schemas/event';
// import { API_URL } from '$env/static/private'; // Will be removed when migration is complete

export const load: LayoutServerLoad = async ({ locals, locals: { safeGetSession, supabase }, cookies }) => {
    const { session } = await safeGetSession();

    if (!locals.user?.club_id) {
        return {
            user: locals.user || null,
            facilities: [],
            fields: [],
            teams: [],
            schedules: [],
            events: [],
            session,
            cookies: cookies.getAll()
        };
    }

    try {
        // Fetch teams from Supabase
        const { data: teams, error: teamsError } = await supabase
            .from('teams')
            .select('*')
            .eq('club_id', locals.user.club_id);

        if (teamsError) {
            console.error('Failed to fetch teams:', teamsError);
            throw error(500, 'Failed to fetch teams');
        }

        // TODO: Implement Supabase queries for these tables
        /*
        const { data: facilities, error: facilitiesError } = await supabase
            .from('facilities')
            .select('*')
            .eq('club_id', locals.user.club_id);

        const { data: fields, error: fieldsError } = await supabase
            .from('fields')
            .select('*')
            .eq('club_id', locals.user.club_id);

        const { data: schedules, error: schedulesError } = await supabase
            .from('schedules')
            .select('*')
            .eq('club_id', locals.user.club_id);

        const { data: events, error: eventsError } = await supabase
            .from('events')
            .select('*')
            .eq('club_id', locals.user.club_id);
        */

        // Temporary: using old API endpoints until migration is complete
        /*const [facilitiesResponse, fieldsResponse, schedulesResponse, eventsResponse] = await Promise.all([
            fetch(`${API_URL}/facilities/club/${locals.user.club_id}`, {
                headers: { 'Authorization': `Bearer ${locals.token}` }
            }),
            fetch(`${API_URL}/fields/club/${locals.user.club_id}`, {
                headers: { 'Authorization': `Bearer ${locals.token}` }
            }),
            fetch(`${API_URL}/schedules/${locals.user.club_id}/schedules`, {
                headers: { 'Authorization': `Bearer ${locals.token}` }
            }),
            fetch(`${API_URL}/events/${locals.user.club_id}`, {
                headers: { 'Authorization': `Bearer ${locals.token}` }
            })
        ]);

        if (!facilitiesResponse.ok) {
            const errorText = await facilitiesResponse.text();
            console.error('Failed to fetch facilities:', facilitiesResponse.status, errorText);
            throw error(facilitiesResponse.status, 'Failed to fetch facilities');
        }

        // ... existing response checks ...

        const facilities: Facility[] = await facilitiesResponse.json();
        const fields: Field[] = await fieldsResponse.json();
        const schedules: Schedule[] = await schedulesResponse.json();
        const events: EventSchedule[] = await eventsResponse.json();*/

        // Temporary empty arrays until Supabase migration is complete
        const facilities: Facility[] = [];
        const fields: Field[] = [];
        const schedules: Schedule[] = [];
        const events: EventSchedule[] = [];
        
        return {
            user: locals.user,
            facilities,
            fields,
            teams: teams || [],
            schedules,
            events,
            session,
            cookies: cookies.getAll()
        };
    } catch (err) {
        console.error('Error in layout load function:', err);
        throw error(500, 'Internal Server Error');
    }
};
