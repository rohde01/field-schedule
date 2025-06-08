import type { PageServerLoad } from './$types';
import { error } from '@sveltejs/kit';
import type { Schedule } from '$lib/schemas/schedule';
import { processFields } from '$lib/utils/fieldProcessor';

export const load: PageServerLoad = async ({ url, locals: { supabase } }) => {
    const hostname = url.hostname;
    const parts = hostname.split('.');
    
    // Check if this is a main domain access (no club subdomain)
    const isMainDomain = hostname === 'baneplanen.info' || 
                        hostname === 'www.baneplanen.info' || 
                        hostname === 'localhost' ||
                        (parts.length === 1); // Single part means localhost or similar
    
    if (isMainDomain) {
        // Fetch all clubs for the dropdown
        const { data: clubs, error: clubsError } = await supabase
            .from('clubs')
            .select('club_id, name, club_url, logo_url')
            .not('club_url', 'is', null)
            .order('name');

        if (clubsError) {
            console.error('Failed to fetch clubs:', clubsError);
            throw error(500, 'Failed to fetch clubs');
        }

        return {
            hasSubdomain: false,
            club: null,
            schedules: [],
            user: null,
            clubs: clubs || [],
            facilities: [],
            fields: [],
            teams: []
        };
    }

    const subdomain = parts[0];

    try {
        // First, find the club by matching subdomain to club_url
        const { data: clubs, error: clubError } = await supabase
            .from('clubs')
            .select('club_id, name, club_url, logo_url')
            .eq('club_url', subdomain)
            .limit(1);

        if (clubError) {
            console.error('Failed to fetch club:', clubError);
            throw error(500, 'Failed to fetch club');
        }

        if (!clubs || clubs.length === 0) {
            // Still fetch all clubs for the dropdown on error page
            const { data: allClubs, error: allClubsError } = await supabase
                .from('clubs')
                .select('club_id, name, club_url')
                .not('club_url', 'is', null)
                .order('name');

            return {
                hasSubdomain: true,
                club: null,
                schedules: [],
                user: null,
                clubs: allClubs || [],
                facilities: [],
                fields: [],
                teams: [],
                invalidSubdomain: subdomain
            };
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

        // Fetch teams for this club
        const { data: teams, error: teamsError } = await supabase
            .from('teams')
            .select('*')
            .eq('club_id', club.club_id);

        if (teamsError) {
            console.error('Failed to fetch teams:', teamsError);
            throw error(500, 'Failed to fetch teams');
        }

        // Fetch fields for this club
        const { data: rawFields, error: fieldsError } = await supabase
            .from('fields')
            .select('*')
            .eq('club_id', club.club_id);

        if (fieldsError) {
            console.error('Failed to fetch fields:', fieldsError);
            throw error(500, 'Failed to fetch fields');
        }

        // Fetch field availabilities from Supabase
        const { data: availabilities, error: availabilityError } = await supabase
            .from('field_availability')
            .select('*')
            .eq('club_id', club.club_id);

        if (availabilityError) {
            console.error('Failed to fetch field availabilities:', availabilityError);
            throw error(500, 'Failed to fetch field availabilities');
        }

        const fields = processFields(rawFields || [], availabilities || []);

        return {
            hasSubdomain: true,
            club,
            schedules,
            user: null,
            clubs: [],
            facilities: [],
            fields: fields || [],
            teams: teams || []
        };
    } catch (err) {
        console.error('Error in root page load function:', err);
        throw error(500, 'Internal Server Error');
    }
};