import type { PageServerLoad } from './$types';
import { error, fail } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms/server';
import { zod } from 'sveltekit-superforms/adapters';
import type { RequestEvent } from '@sveltejs/kit';

import { generateScheduleRequestSchema, type Schedule } from '$lib/schemas/schedule';

export const load = (async ({ fetch, locals }: RequestEvent) => {
    const createScheduleForm = await superValidate(zod(generateScheduleRequestSchema), {
        id: 'schedule-form',
        defaults: {
            facility_id: 0,
            team_ids: [],
            constraints: [],
            club_id: locals.user?.primary_club_id ?? 0,
            schedule_name: 'Generated Schedule'
        }
    });

    if (!locals.user) {
        throw error(401, 'Unauthorized');
    }

    try {
        const response = await fetch(`http://localhost:8000/schedules/${locals.user.primary_club_id}/schedules`, {
            headers: {
                'Authorization': `Bearer ${locals.token}`
            }
        });
        if (!response.ok) throw new Error('Failed to fetch schedules');
        const schedules: Schedule[] = await response.json();
        console.log('Fetched schedules:', schedules);
        
        return {
            schedules,
            form: createScheduleForm
        };
    } catch (e) {
        throw error(500, 'Error loading schedules');
    }
}) satisfies PageServerLoad;

export const actions = {
    createSchedule: async ({ request, fetch, locals }: RequestEvent) => {
        // Use superValidate with the request directly to handle JSON data
        const form = await superValidate(request, zod(generateScheduleRequestSchema));

        console.log('Form validation result:', form);
        
        if (!form.valid) {
            console.log('Form validation failed:', form.errors);
            return fail(400, { form });
        }

        try {
            const response = await fetch('http://localhost:8000/schedules/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${locals.token}`
                },
                body: JSON.stringify(form.data)
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error('Failed to create schedule:', response.status, errorData);
                return fail(response.status, { 
                    form, 
                    error: errorData.detail || 'Failed to create schedule'
                });
            }

            const data = await response.json();
            console.log('API Response:', response.status, data);

            return { 
                form,
                success: true,
                schedule_id: data.schedule_id
            };
        } catch (err) {
            console.error('API call failed:', err);
            return fail(500, { 
                form, 
                error: 'Failed to create schedule' 
            });
        }
    }
};