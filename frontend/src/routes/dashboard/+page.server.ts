import { error, fail } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { activeScheduleCreateSchema, activeScheduleUpdateSchema } from '$lib/schemas/schedule';
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
            const validated = activeScheduleCreateSchema.parse(data);
            const res = await fetch(`${API_URL}/active-schedules`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${locals.token}`
                },
                body: JSON.stringify(validated)
            });

            if (!res.ok) return fail(res.status, { error: 'Failed to create active schedule' });
            return { success: true, data: await res.json() };
        } catch (err) {
            return fail(400, { error: 'Invalid data' });
        }
    },

    updateActiveSchedule: async ({ request, fetch, locals }) => {
        const data = Object.fromEntries(await request.formData());
        const activeScheduleId = data.activeScheduleId;
        
        try {
            const validated = activeScheduleUpdateSchema.parse(data);
            const res = await fetch(`${API_URL}/active-schedules/${activeScheduleId}`, {
                method: 'PUT',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${locals.token}`
                },
                body: JSON.stringify(validated)
            });

            if (!res.ok) return fail(res.status, { error: 'Failed to update active schedule' });
            return { success: true, data: await res.json() };
        } catch (err) {
            return fail(400, { error: 'Invalid data' });
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

            if (!res.ok) return fail(res.status, { error: 'Failed to delete active schedule' });
            return { success: true, data: await res.json() };
        } catch (err) {
            return fail(500, { error: 'Failed to delete active schedule' });
        }
    }
} satisfies Actions;