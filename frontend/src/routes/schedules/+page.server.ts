import type { PageServerLoad, Actions } from './$types';
import { error, fail } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms/server';
import { zod } from 'sveltekit-superforms/adapters';
import type { RequestEvent } from '@sveltejs/kit';
import { generateScheduleRequestSchema, deleteScheduleSchema, type Schedule, type DeleteScheduleResponse } from '$lib/schemas/schedule';
import { API_URL } from '$env/static/private';

export const load = (async ({ fetch, locals }: RequestEvent) => {
    const createScheduleForm = await superValidate(zod(generateScheduleRequestSchema), {
        id: 'schedule-form',
        defaults: {
            facility_id: 0,
            team_ids: [],
            constraints: [],
            club_id: locals.user?.primary_club_id ?? 0,
            schedule_name: ''
        }
    });

    const deleteScheduleForm = await superValidate(zod(deleteScheduleSchema), {
        id: 'delete-schedule-form'
    });

    if (!locals.user) {
        throw error(401, 'Unauthorized');
    }

    try {
        const response = await fetch(`${API_URL}/schedules/${locals.user.primary_club_id}/schedules`, {
            headers: {
                'Authorization': `Bearer ${locals.token}`
            }
        });
        if (!response.ok) throw new Error('Failed to fetch schedules');
        const schedules: Schedule[] = await response.json();
        
        return {
            schedules,
            form: createScheduleForm,
            deleteForm: deleteScheduleForm
        };
    } catch (e) {
        throw error(500, 'Error loading schedules');
    }
}) satisfies PageServerLoad;

export const actions = {
    createSchedule: async ({ request, fetch, locals }: RequestEvent) => {
        const form = await superValidate(request, zod(generateScheduleRequestSchema));
        
        if (!form.valid) {
            return fail(400, { form });
        }

        try {
            const response = await fetch(`${API_URL}/schedules/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${locals.token}`
                },
                body: JSON.stringify(form.data)
            });

            if (!response.ok) {
                const errorData = await response.json();
                return fail(response.status, { 
                    form,
                    errors: {
                        _errors: [errorData.detail || 'Failed to create schedule']
                    }
                });
            }

            const data = await response.json();

            return { 
                form,
                success: true,
                schedule_id: data.schedule_id
            };
        } catch (err) {
            return fail(500, { 
                form,
                errors: {
                    _errors: ['An unexpected error occurred while creating the schedule']
                }
            });
        }
    },

    deleteSchedule: async ({ request, fetch, locals }: RequestEvent) => {
        const form = await superValidate(request, zod(deleteScheduleSchema));

        if (!form.valid) {
            return fail(400, { form });
        }

        try {
            const response = await fetch(`${API_URL}/schedules/delete/${form.data.schedule_id}`, {
                method: 'DELETE', 
                headers: {
                    'Authorization': `Bearer ${locals.token}`
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                return fail(response.status, { 
                    form,
                    error: errorData.detail || 'Failed to delete schedule'
                });
            }

            const result: DeleteScheduleResponse = await response.json();

            return { 
                form,
                success: true,
                message: result.message,
                action: result.action
            };
        } catch (err) {
            return fail(500, { 
                form,
                error: 'Failed to delete schedule' 
            });
        }
    },

    updateEntry: async ({ request, fetch, locals }) => {
        const formData = await request.formData();
        const entryId = parseInt(formData.get('entryId') as string);
        
        const changes: Record<string, any> = {};
        formData.forEach((value, key) => {
            if (key !== 'entryId') {
                changes[key] = value;
            }
        });

        try {
            const response = await fetch(`${API_URL}/schedules/entry/${entryId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${locals.token}`
                },
                body: JSON.stringify(changes)
            });

            if (!response.ok) {
                const error = await response.json();
                return fail(response.status, { error: error.detail });
            }

            return { success: true };
        } catch (err) {
            return fail(500, { error: 'Failed to update schedule entry' });
        }
    },

    createEntry: async ({ request, fetch, locals }: RequestEvent) => {
        const formData = await request.formData();
        const scheduleId = Number(formData.get('scheduleId'));
        const entry: Record<string, any> = {};
        formData.forEach((value, key) => {
            if (key.startsWith('entry.')) {
                entry[key.replace('entry.', '')] = value;
            }
        });

        try {
            const response = await fetch(`${API_URL}/schedules/entry`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${locals.token}`
                },
                body: JSON.stringify({ schedule_id: scheduleId, entry })
            });

            if (!response.ok) {
                const errorData = await response.json();
                return fail(response.status, { error: errorData.detail || 'Failed to create schedule entry' });
            }

            const result = await response.json();
            return { success: true, schedule_entry_id: result.schedule_entry_id };
        } catch (err) {
            return fail(500, { error: 'Failed to create schedule entry' });
        }
    },

    deleteEntry: async ({ request, fetch, locals }: RequestEvent) => {
        const formData = await request.formData();
        const entryId = parseInt(formData.get('entryId') as string);

        try {
            const response = await fetch(`${API_URL}/schedules/entry/${entryId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${locals.token}`
                }
            });

            if (!response.ok) {
                const error = await response.json();
                return fail(response.status, { error: error.detail });
            }

            return { success: true, entryId };
        } catch (err) {
            return fail(500, { error: 'Failed to delete schedule entry' });
        }
    }
} satisfies Actions;


