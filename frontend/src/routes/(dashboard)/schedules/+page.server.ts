import type { Actions } from './$types';
import type { ScheduleEntry } from '$lib/schemas/schedule';
import { error } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms/server';
import { zod } from 'sveltekit-superforms/adapters';
import type { RequestEvent } from '@sveltejs/kit';
import { generateScheduleRequestSchema, deleteScheduleSchema, scheduleEntrySchema } from '$lib/schemas/schedule';
import { fail } from '@sveltejs/kit';

export const ssr = false;

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
    insertScheduleEntries: async ({ request, locals }) => {
        if (!locals.user) throw error(401, 'Unauthorized');
        const formData = await request.formData();
        const entries = JSON.parse(formData.get('entries') as string || '[]');
        const scheduleId = Number(formData.get('scheduleId'));
        if (!scheduleId) return fail(400, { message: 'Missing required data' });
        const toInsert = entries.filter((e: ScheduleEntry) => !e.schedule_entry_id);
        if (toInsert.length) {
            const { error: insertError } = await locals.supabase.from('schedule_entries').insert(
                toInsert.map((e: ScheduleEntry) => {
                    const { schedule_entry_id, ...payload } = e;
                    return { ...payload, schedule_id: scheduleId };
                })
            );
            if (insertError) {
                return fail(500, { message: 'Insert failed', error: insertError.message });
            }
        }
        return { success: true };
    },
    updateScheduleEntries: async ({ request, locals }) => {
        if (!locals.user) throw error(401, 'Unauthorized');
        const formData = await request.formData();
        const entries = JSON.parse(formData.get('entries') as string || '[]');
        const scheduleId = Number(formData.get('scheduleId'));
        if (!scheduleId) return fail(400, { message: 'Missing required data' });
        const toUpdate = entries.filter((e: ScheduleEntry) => e.schedule_entry_id);
        if (toUpdate.length) {
            const { error: updateError } = await locals.supabase.from('schedule_entries').upsert(
                toUpdate.map((e: ScheduleEntry) => ({ ...e, schedule_id: scheduleId })),
                { onConflict: 'schedule_entry_id' }
            );
            if (updateError) return fail(500, { message: 'Update failed', error: updateError });
        }
        return { success: true };
    },
    deleteScheduleEntries: async ({ request, locals }) => {
        if (!locals.user) throw error(401, 'Unauthorized');
        const formData = await request.formData();
        const deleteIds: number[] = JSON.parse(formData.get('deleteIds') as string || '[]');
        if (deleteIds.length) {
            const { error: deleteError } = await locals.supabase
                .from('schedule_entries')
                .delete()
                .in('schedule_entry_id', deleteIds);
            if (deleteError) return fail(500, { message: 'Delete failed', error: deleteError.message });
        }
        return { success: true };
    }
} satisfies Actions;
