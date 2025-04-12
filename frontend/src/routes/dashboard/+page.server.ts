import { error, fail } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { activeScheduleUpdateSchema } from '$lib/schemas/schedule';
import { API_URL } from '$env/static/private';

export const load = (async ({ fetch, locals }) => {
    if (!locals.user?.club_id) throw error(403, 'No club access');

    try {
        const res = await fetch(`${API_URL}/active-schedules/${locals.user.club_id}`, {
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
    },

    createEventOverride: async ({ request, fetch, locals }) => {
        if (!locals.user) return fail(403, { error: 'Not authenticated' });
        
        const formData = Object.fromEntries(await request.formData());
        
        try {
            const rawData = {
                active_schedule_id: parseInt(formData.active_schedule_id as string),
                override_date: formData.override_date as string,
                new_start_time: formData.new_start_time as string,
                new_end_time: formData.new_end_time as string,
                new_team_id: formData.new_team_id ? parseInt(formData.new_team_id as string) : null,
                new_field_id: formData.new_field_id ? parseInt(formData.new_field_id as string) : null,
                schedule_entry_id: formData.schedule_entry_id ? parseInt(formData.schedule_entry_id as string) : null,
                is_deleted: formData.is_deleted === 'true'
            };
            
            const validatedData = EventOverrideCreateSchema.parse(rawData);
            
            const res = await fetch(`${API_URL}/events/override`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${locals.token}`
                },
                body: JSON.stringify(validatedData)
            });

            if (!res.ok) {
                const errorText = await res.text();
                return fail(res.status, { error: `Failed to create event override: ${errorText}` });
            }
            
            const result = await res.json();
            return { override_id: result.override_id };
        } catch (err) {
            return fail(400, { error: `Invalid data: ${err}` });
        }
    },

    updateEventOverride: async ({ request, fetch, locals }) => {
        if (!locals.user) return fail(403, { error: 'Not authenticated' });
        
        const formData = Object.fromEntries(await request.formData());
        const overrideId = formData.override_id;
        
        try {
            const updateFields: Record<string, any> = {};
            
            if (formData.new_start_time) updateFields.new_start_time = formData.new_start_time;
            if (formData.new_end_time) updateFields.new_end_time = formData.new_end_time;
            if (formData.override_date) updateFields.override_date = formData.override_date;
            if ('new_team_id' in formData) {
                updateFields.new_team_id = formData.new_team_id 
                    ? parseInt(formData.new_team_id as string) 
                    : null;
            }
            if ('new_field_id' in formData) {
                updateFields.new_field_id = formData.new_field_id 
                    ? parseInt(formData.new_field_id as string) 
                    : null;
            }
            if ('is_deleted' in formData) {
                updateFields.is_deleted = formData.is_deleted === 'true';
            }
            
            const validatedData = EventOverrideUpdateSchema.parse({
                override_id: parseInt(overrideId as string),
                ...updateFields
            });
            
            const res = await fetch(`${API_URL}/events/override/${overrideId}`, {
                method: 'PUT',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${locals.token}`
                },
                body: JSON.stringify(updateFields)
            });

            if (!res.ok) {
                const errorText = await res.text();
                return fail(res.status, { error: `Failed to update event override: ${errorText}` });
            }
            
            return { success: true, data: await res.json() };
        } catch (err) {
            return fail(400, { error: `Invalid data: ${err}` });
        }
    },

    deleteEventOverride: async ({ request, fetch, locals }) => {
        if (!locals.user) return fail(403, { error: 'Not authenticated' });
        
        const formData = Object.fromEntries(await request.formData());
        const overrideId = formData.override_id;
        
        try {
            const res = await fetch(`${API_URL}/events/override/${overrideId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${locals.token}`
                }
            });

            if (!res.ok) {
                const errorText = await res.text();
                return fail(res.status, { error: `Failed to delete event override: ${errorText}` });
            }
            
            return { success: true, data: await res.json() };
        } catch (err) {
            return fail(500, { error: 'Failed to delete event override' });
        }
    }
} satisfies Actions;