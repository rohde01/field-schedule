import type { Actions } from './$types';
import type { ScheduleEntry } from '$lib/schemas/schedule';
import { error } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms/server';
import { zod } from 'sveltekit-superforms/adapters';
import type { RequestEvent } from '@sveltejs/kit';
import { deleteScheduleSchema, createScheduleSchema, type CreateScheduleInput } from '$lib/schemas/schedule';
import { fail } from '@sveltejs/kit';

export const ssr = false;

export const load = (async ({ locals }: RequestEvent) => {

    const deleteScheduleForm = await superValidate(zod(deleteScheduleSchema), {
        id: 'delete-schedule-form'
    });
    const createScheduleForm = await superValidate(zod(createScheduleSchema), {
        id: 'create-schedule-form'
    });

    if (!locals.user) {
        throw error(401, 'Unauthorized');
    }

    return {
        deleteForm: deleteScheduleForm,
        createForm: createScheduleForm
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
    },
    createSchedule: async ({ request, locals }) => {
        if (!locals.user) throw error(401, 'Unauthorized');
        
        const form = await superValidate(request, zod(createScheduleSchema));
        if (!form.valid) return fail(400, { form });

        const data: CreateScheduleInput = form.data;
        const { data: newSchedule, error: insertError } = await locals.supabase
            .from('schedules')
            .insert(data)
            .select()
            .single();
            
        if (insertError) return fail(500, { form, message: 'Schedule creation failed', error: insertError.message });
        
        return { form, success: true, schedule: newSchedule };
    }
} satisfies Actions;
