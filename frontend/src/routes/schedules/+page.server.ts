import type { Actions } from './$types';
import { error } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms/server';
import { zod } from 'sveltekit-superforms/adapters';
import type { RequestEvent } from '@sveltejs/kit';
import { generateScheduleRequestSchema, deleteScheduleSchema } from '$lib/schemas/schedule';

export const load = (async ({ locals }: RequestEvent) => {
    const createScheduleForm = await superValidate(zod(generateScheduleRequestSchema), {
        id: 'schedule-form',
        defaults: {
            facility_id: 0,
            team_ids: [],
            constraints: [],
            club_id: locals.user?.club_id ?? 0,
            schedule_name: ''
        }
    });

    const deleteScheduleForm = await superValidate(zod(deleteScheduleSchema), {
        id: 'delete-schedule-form'
    });

    if (!locals.user) {
        throw error(401, 'Unauthorized');
    }

    return {
        form: createScheduleForm,
        deleteForm: deleteScheduleForm
    };
}) 

export const actions = {


} satisfies Actions;


