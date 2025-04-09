import type { LayoutServerLoad } from './$types';
import { error } from '@sveltejs/kit';
import type { Schedule } from '$lib/schemas/schedule';
import type { EventSchedule } from '$lib/schemas/event';
import { processFields } from '$lib/utils/fieldProcessor';

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

        // Fetch facilities from Supabase
        const { data: facilities, error: facilitiesError } = await supabase
            .from('facilities')
            .select('*')
            .eq('club_id', locals.user.club_id);

        if (facilitiesError) {
            console.error('Failed to fetch facilities:', facilitiesError);
            throw error(500, 'Failed to fetch facilities');
        }

        // Fetch fields from Supabase
        const { data: rawFields, error: fieldsError } = await supabase
            .from('fields')
            .select('*')
            .eq('club_id', locals.user.club_id);

        if (fieldsError) {
            console.error('Failed to fetch fields:', fieldsError);
            throw error(500, 'Failed to fetch fields');
        }

        // Fetch field availabilities from Supabase
        const { data: availabilities, error: availabilityError } = await supabase
            .from('field_availability')
            .select('*')
            .eq('club_id', locals.user.club_id);

        if (availabilityError) {
            console.error('Failed to fetch field availabilities:', availabilityError);
            throw error(500, 'Failed to fetch field availabilities');
        }

        const fields = processFields(rawFields || [], availabilities || []);

        // Temporary empty arrays for schedules and events until Supabase migration is complete
        const schedules: Schedule[] = [];
        const events: EventSchedule[] = [];
        
        return {
            user: locals.user,
            facilities: facilities || [],
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