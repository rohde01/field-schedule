import type { PageServerLoad } from './$types';
import { error } from '@sveltejs/kit';
import type { Schedule } from '$lib/schemas/schedule';

export const load: PageServerLoad = async ({ url, locals: { supabase } }) => {
    const hostname = url.hostname;
    const parts = hostname.split('.');
    const hasSubdomain = parts.length > 1 && parts[0] !== 'localhost' && parts[0] !== 'www';
    
    console.log(`[Public View] Analyzing hostname: ${hostname}, parts:`, parts);
    console.log(`[Public View] Has subdomain: ${hasSubdomain}`);
    
    if (!hasSubdomain) {
        console.log('[Public View] No subdomain detected - showing landing page');
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
    console.log(`[Public View] Subdomain detected: "${subdomain}" - fetching all schedules from database`);

    try {
        // Fetch ALL schedules from the entire database
        console.log(`[Public View] Fetching ALL schedules across all clubs`);
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
            `);

        if (schedulesError) {
            console.error('Failed to fetch schedules:', schedulesError);
            throw error(500, 'Failed to fetch schedules');
        }

        const schedules: Schedule[] = rawSchedules || [];
        console.log(`[Public View] Found ${schedules.length} total schedules across all clubs`);

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