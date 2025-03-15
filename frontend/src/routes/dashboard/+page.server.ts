import { error, fail } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { activeScheduleUpdateSchema } from '$lib/schemas/schedule';
import { API_URL } from '$env/static/private';

export const load = (async ({ fetch, locals }) => {
    if (!locals.user?.primary_club_id) throw error(403, 'No club access');

    try {
        const res = await fetch(`${API_URL}/active-schedules/${locals.user.primary_club_id}`, {
            headers: {
                'Authorization': `Bearer ${locals.token}`
            }
        });
        if (!res.ok) throw error(res.status, 'Failed to fetch active schedules');

        const activeSchedules = await res.json();

        return {
            firstName: locals.user?.firstName || 'Guest',
            activeSchedules
        };
    } catch (err) {
        throw error(500, 'Failed to load active schedules');
    }
}) satisfies PageServerLoad;

export const actions = {
    createActiveSchedule: async ({ request, fetch, locals }) => {
        const data = Object.fromEntries(await request.formData());
        
        try {
            
            const validatedData = {
                club_id: locals.user.primary_club_id,
                schedule_id: parseInt(data.schedule_id as string),
                start_date: new Date(data.start_date as string).toISOString().split('T')[0],
                end_date: new Date(data.end_date as string).toISOString().split('T')[0]
            };
            
            console.log("Sending to API:", validatedData);
            
            const res = await fetch(`${API_URL}/active-schedules`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${locals.token}`
                },
                body: JSON.stringify(validatedData)
            });

            if (!res.ok) {
                const errorText = await res.text();
                return fail(res.status, { error: `Failed to create active schedule: ${errorText}` });
            }
            return { success: true, data: await res.json() };
        } catch (err) {
            return fail(400, { error: 'Invalid data for creating active schedule' });
        }
    },

    updateActiveSchedule: async ({ request, fetch, locals }) => {
        const data = Object.fromEntries(await request.formData());
        const activeScheduleId = data.activeScheduleId;
        
        try {
            const formattedData = {
                schedule_id: parseInt(data.schedule_id as string),
                start_date: new Date(data.start_date as string).toISOString().split('T')[0],
                end_date: new Date(data.end_date as string).toISOString().split('T')[0]
            };
            
            const validated = activeScheduleUpdateSchema.parse(formattedData);
            const res = await fetch(`${API_URL}/active-schedules/${activeScheduleId}`, {
                method: 'PUT',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${locals.token}`
                },
                body: JSON.stringify(validated)
            });

            if (!res.ok) {
                const errorText = await res.text();
                return fail(res.status, { error: `Failed to update active schedule: ${errorText}` });
            }
            return { success: true, data: await res.json() };
        } catch (err) {
            return fail(400, { error: `Invalid data: ${err}` });
        }
    },

    deleteActiveSchedule: async ({ request, fetch, locals }) => {
        const data = Object.fromEntries(await request.formData());
        const activeScheduleId = data.activeScheduleId;

        try {
            const res = await fetch(`${API_URL}/active-schedules/${activeScheduleId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${locals.token}`
                }
            });

            if (!res.ok) {
                return fail(res.status, { error: 'Failed to delete active schedule' });
            }
            return { success: true, data: await res.json() };
        } catch (err) {
            return fail(500, { error: 'Failed to delete active schedule' });
        }
    }
} satisfies Actions;