import type { Actions } from './$types';
import { fail } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms/server';
import { zod } from 'sveltekit-superforms/adapters';
import { facilityCreateSchema } from '$lib/schemas/facility';
import { deleteFieldSchema, fieldCreateSchema, updateFieldSchema } from '$lib/schemas/field';
export const ssr = false

export const load = async ({ locals }) => {
    const [facilityForm, deleteForm, createFieldForm, updateFieldForm] = await Promise.all([
        superValidate(zod(facilityCreateSchema), {
            id: 'facility-form',
            defaults: {
                name: '',
                description: '',
                address: '',
                is_primary: false,
                club_id: locals.user?.club_id ?? 0
            }
        }),
        superValidate(zod(deleteFieldSchema), {
            id: 'delete-field-form'
        }), 
        superValidate(zod(fieldCreateSchema), {
            id: 'field-form',
            defaults: {
                facility_id: 0,
                name: '',
                size: '11v11',
                field_type: 'full',
                half_fields: [],
                availabilities: []
            }
        }),
        superValidate(zod(updateFieldSchema), {
            id: 'update-field-form'
        })
    ]);
        return {
            facilityForm,
            createFieldForm,
            updateFieldForm,
            deleteForm,
        };
 
};

// action for creating a facility
export const actions: Actions = {
    create: async ({ request, locals: { supabase, user } }) => {
        const form = await superValidate(request, zod(facilityCreateSchema));
        console.log('Form validation result:', form);
        
        const clubId = user?.club_id;
        if (!clubId || clubId <= 0) {
            console.log('Invalid club_id:', clubId);
            return fail(400, { 
                form,
                error: 'Invalid club ID'
            });
        }

        form.data.club_id = clubId;
        
        const validatedForm = await superValidate(form.data, zod(facilityCreateSchema));
        if (!validatedForm.valid) {
            return fail(400, { form: validatedForm });
        }

        try {
            const { data: facility, error: insertError } = await supabase
                .from('facilities')
                .insert(validatedForm.data)
                .select()
                .single();

            if (insertError) {
                return fail(400, { 
                    form,
                    error: insertError.message || 'Failed to create facility'
                });
            }
            
            return {
                form,
                facility,
                success: true
            };
        } catch (err) {
            console.error('Error creating facility:', err);
            return fail(500, { 
                form, 
                error: 'Failed to create facility'
            });
        }
    },

    // action for creating a field
    createField: async ({ request, locals: { supabase, user } }) => {
        console.log('CreateField action started');

        // Use superValidate with the request directly to handle JSON data
        const form = await superValidate(request, zod(fieldCreateSchema));
        
        if (!form.valid) {
            return fail(400, { form });
        }
        
        const clubId = user?.club_id;

        try {
            // Start a Supabase transaction
            const { data: mainField, error: mainFieldError } = await supabase
                .from('fields')
                .insert({
                    facility_id: form.data.facility_id,
                    club_id: clubId,
                    name: form.data.name,
                    size: form.data.size,
                    field_type: form.data.field_type,
                    parent_field_id: null,
                    is_active: true
                })
                .select()
                .single();

            if (mainFieldError) {
                console.error('Failed to create field:', mainFieldError);
                return fail(400, { form, error: 'Failed to create field' });
            }

            const mainFieldId = mainField.field_id;
            const halfFieldIds: number[] = [];

            // Insert half fields if any
            if (form.data.half_fields && form.data.half_fields.length > 0) {
                for (const halfField of form.data.half_fields) {
                    const { data: insertedHalfField, error: halfFieldError } = await supabase
                        .from('fields')
                        .insert({
                            facility_id: form.data.facility_id,
                            club_id: clubId,
                            name: halfField.name,
                            size: form.data.size,
                            field_type: halfField.field_type,
                            parent_field_id: mainFieldId,
                            is_active: true
                        })
                        .select()
                        .single();

                    if (halfFieldError) {
                        console.error('Failed to create field hierarchy:', halfFieldError);
                        return fail(400, { form, error: 'Failed to create field' });
                    }

                    halfFieldIds.push(insertedHalfField.field_id);

                    // Insert quarter fields if any
                    if (halfField.quarter_fields && halfField.quarter_fields.length > 0) {
                        for (const quarterField of halfField.quarter_fields) {
                            const { error: quarterFieldError } = await supabase
                                .from('fields')
                                .insert({
                                    facility_id: form.data.facility_id,
                                    club_id: clubId,
                                    name: quarterField.name,
                                    size: form.data.size,
                                    field_type: quarterField.field_type,
                                    parent_field_id: insertedHalfField.field_id,
                                    is_active: true
                                });

                            if (quarterFieldError) {
                                console.error('Failed to create field hierarchy:', quarterFieldError);
                                return fail(400, { form, error: 'Failed to create field' });
                            }
                        }
                    }
                }
            }

            // Insert availabilities if any
            if (form.data.availabilities && form.data.availabilities.length > 0) {
                const availabilitiesToInsert = form.data.availabilities.map(availability => ({
                    field_id: mainFieldId,
                    club_id: clubId,
                    day_of_week: availability.day_of_week,
                    start_time: availability.start_time,
                    end_time: availability.end_time
                }));

                const { error: availabilityError } = await supabase
                    .from('field_availability')
                    .insert(availabilitiesToInsert);

                if (availabilityError) {
                    console.error('Failed to create field availabilities:', availabilityError);
                    return fail(400, { form, error: 'Failed to create field' });
                }
            }

            return { 
                form,
                success: true,
                field: mainField
            };
        } catch (err) {
            console.error('Error creating field:', err);
            return fail(500, { form, error: 'Failed to create field' });
        }
    },

    // action for updating a field
    updateField: async ({ request, locals: { supabase, user } }) => {
        const form = await superValidate(request, zod(updateFieldSchema));
        
        if (!form.valid) {
            return fail(400, { form });
        }

        try {
            const { data: field, error: updateError } = await supabase
                .from('fields')
                .update({
                    name: form.data.name,
                    size: form.data.size,
                    is_active: form.data.is_active
                })
                .eq('field_id', form.data.field_id)
                .select()
                .single();

            if (updateError) {
                console.error('Failed to update field:', updateError);
                return fail(400, { 
                    form,
                    error: updateError.message || 'Failed to update field'
                });
            }

            return { 
                form,
                success: true,
                field,
                action: 'update'
            };
        } catch (err) {
            console.error('Error updating field:', err);
            return fail(500, { 
                form,
                error: 'Failed to update field'
            });
        }
    },

    deleteField: async ({ request, locals: { supabase } }) => {
        const form = await superValidate(request, zod(deleteFieldSchema));

        if (!form.valid) {
            return fail(400, { form });
        }

        try {
            // Delete the field - the cascade will handle child fields and availabilities
            const { error: deleteError } = await supabase
                .from('fields')
                .delete()
                .eq('field_id', form.data.field_id);

            if (deleteError) {
                console.error('Failed to delete field:', deleteError);
                return fail(400, { 
                    form,
                    error: 'Failed to delete the field'
                });
            }

            return { 
                form,
                success: true,
                message: 'Field successfully deleted.',
                action: 'deleted field'
            };
        } catch (err) {
            console.error('Error deleting field:', err);
            return fail(500, { 
                form,
                error: 'Failed to delete field' 
            });
        }
    }
} satisfies Actions;
