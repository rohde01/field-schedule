import type { PageServerLoad } from './$types';
import { error } from '@sveltejs/kit';
import type { Schedule } from '$lib/schemas/schedule';

export const load: PageServerLoad = async ({ url, locals: { supabase } }) => {
    const hostname = url.hostname;
    const parts = hostname.split('.');
    const hasSubdomain = parts.length > 1 && parts[0] !== 'localhost' && parts[0] !== 'www';
    
    if (!hasSubdomain) {
        return {
            hasSubdomain: false,
            club: null,
            schedules: [],
            user: null,
            clubs: [],
            facilities: [],
            fields: [],
            teams: []
        };
    }

    const subdomain = parts[0];

    try {
        // First, find the club by matching subdomain to club name
        const { data: clubs, error: clubError } = await supabase
            .from('clubs')
            .select('club_id, name')
            .eq('name', subdomain)
            .limit(1);

        if (clubError) {
            console.error('Failed to fetch club:', clubError);
            throw error(500, 'Failed to fetch club');
        }

        if (!clubs || clubs.length === 0) {
            throw error(404, 'Club not found');
        }

        const club = clubs[0];

        // Now fetch schedules for this specific club
        const { data: rawSchedules, error: schedulesError } = await supabase
            .from('schedules')
            .select(`
                schedule_id,
                club_id,
                facility_id,
                name,
                created_at,
                active_from,
                active_until,
                description,
                schedule_entries (
                    schedule_entry_id,
                    schedule_id,
                    uid,
                    team_id,
                    field_id,
                    dtstart,
                    dtend,
                    recurrence_rule,
                    recurrence_id,
                    exdate,
                    summary,
                    description
                )
            `)
            .eq('club_id', club.club_id);

        if (schedulesError) {
            console.error('Failed to fetch schedules:', schedulesError);
            throw error(500, 'Failed to fetch schedules');
        }

        const schedules: Schedule[] = rawSchedules || [];
        console.log(`[Public View] Found ${schedules.length} schedules for club: ${club.name}`);

        return {
            hasSubdomain: true,
            club: null,
            schedules,
            user: null,
            clubs: [],
            facilities: [],
            fields: [],
            teams: []
        };
    } catch (err) {
        console.error('Error in root page load function:', err);
        throw error(500, 'Internal Server Error');
    }
};