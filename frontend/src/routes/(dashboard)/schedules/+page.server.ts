import type { Actions } from './$types';
import type { ScheduleEntry } from '$lib/schemas/schedule';
import { error } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms/server';
import { zod } from 'sveltekit-superforms/adapters';
import type { RequestEvent } from '@sveltejs/kit';
import { deleteScheduleSchema, createScheduleSchema, updateScheduleSchema, type CreateScheduleInput, type UpdateScheduleInput } from '$lib/schemas/schedule';
import { fail } from '@sveltejs/kit';

export const ssr = false;

export const load = (async ({ locals }: RequestEvent) => {

    const deleteScheduleForm = await superValidate(zod(deleteScheduleSchema), {
        id: 'delete-schedule-form'
    });
    const createScheduleForm = await superValidate(zod(createScheduleSchema), {
        id: 'create-schedule-form'
    });
    const updateForm = await superValidate(zod(updateScheduleSchema), {
        id: 'update-schedule-form'
    });

    if (!locals.user) {
        throw error(401, 'Unauthorized');
    }

    return {
        deleteForm: deleteScheduleForm,
        createForm: createScheduleForm,
        updateForm
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

        const data = form.data;
        const scheduleEntries = data.schedule_entries || [];
        
        // Remove schedule_entries before inserting schedule
        const { schedule_entries, ...scheduleData } = data;
        
        // Create the schedule
        const { data: newSchedule, error: insertError } = await locals.supabase
            .from('schedules')
            .insert(scheduleData)
            .select()
            .single();
            
        if (insertError) return fail(500, { form, message: 'Schedule creation failed', error: insertError.message });
        
        // If there are schedule entries to save
        if (scheduleEntries.length > 0) {
            // Add schedule_id to each entry
            const entriesToInsert = scheduleEntries.map((entry: ScheduleEntry) => {
                const { schedule_entry_id, ...entryData } = entry;
                return { ...entryData, schedule_id: newSchedule.schedule_id };
            });
            
            // Insert the entries
            const { error: entriesError } = await locals.supabase
                .from('schedule_entries')
                .insert(entriesToInsert);
                
            if (entriesError) {
                return fail(500, { 
                    form, 
                    message: 'Schedule created but failed to save entries', 
                    error: entriesError.message,
                    schedule: newSchedule
                });
            }
        }
        
        // Fetch the complete schedule with entries after creation
        const { data: completeSchedule, error: fetchError } = await locals.supabase
            .from('schedules')
            .select(`
                *,
                schedule_entries(*)
            `)
            .eq('schedule_id', newSchedule.schedule_id)
            .single();
            
        if (fetchError) {
            return fail(500, { 
                form, 
                message: 'Schedule created but failed to fetch complete data', 
                error: fetchError.message,
                schedule: newSchedule
            });
        }
        
        return { form, success: true, schedule: completeSchedule };
    },
    updateSchedule: async ({ request, locals }) => {
        if (!locals.user) throw error(401, 'Unauthorized');
        const form = await superValidate(request, zod(updateScheduleSchema));
        if (!form.valid) return fail(400, { form });

        const { schedule_id, name, description, active_from, active_until } = form.data as UpdateScheduleInput;
        const { data: updatedSchedule, error: updateError } = await locals.supabase
            .from('schedules')
            .update({ name, description, active_from, active_until })
            .eq('schedule_id', schedule_id)
            .select()
            .single();
        
        if (updateError) {
            let errorMessage = 'Schedule update failed';
            
            // Provide user-friendly error messages for specific constraint violations
            if (updateError.message?.includes('no_overlapping_active_windows')) {
                errorMessage = 'Schedule dates overlap with another active schedule. Please choose different dates.';
            }
            
            form.message = errorMessage;
            return fail(500, { form, message: errorMessage, error: updateError.message });
        }

        // Set message on the form object for superforms
        form.message = 'Schedule updated successfully!';
        return { form, success: true, schedule: updatedSchedule };
    }
} satisfies Actions;
