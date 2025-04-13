import type { LayoutServerLoad } from './$types';
import { error } from '@sveltejs/kit';
import type { Schedule } from '$lib/schemas/schedule';
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

        // Fetch schedules and join schedule_entries from Supabase
        const { data: rawSchedules, error: schedulesError } = await supabase
            .from('schedules')
            .select(`
                schedule_id,
                club_id,
                facility_id,
                name,
                active_from,
                active_until,
                schedule_entries (
                    schedule_entry_id,
                    schedule_id,
                    team_id,
                    field_id,
                    dtstart,
                    dtend,
                    recurrence_rule,
                    recurrence_id,
                    recurring_entry_id,
                    exdate,
                    summary,
                    description
                )
            `)
            .eq('club_id', locals.user.club_id);

        if (schedulesError) {
            console.error('Failed to fetch schedules:', schedulesError);
            throw error(500, 'Failed to fetch schedules');
        }

        const schedules: Schedule[] = rawSchedules || [];

        
        return {
            user: locals.user,
            facilities: facilities || [],
            fields,
            teams: teams || [],
            schedules,
            session,
            cookies: cookies.getAll()
        };
    } catch (err) {
        console.error('Error in layout load function:', err);
        throw error(500, 'Internal Server Error');
    }
};
