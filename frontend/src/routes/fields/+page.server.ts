import type { PageServerLoad, Actions } from './$types';
import { error, fail } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms/server';
import { zod } from 'sveltekit-superforms/adapters';
import { facilityCreateSchema } from '$lib/schemas/facility';
import { deleteFieldSchema, fieldCreateSchema, type DeleteFieldResponse } from '$lib/schemas/field';
import { API_URL } from '$env/static/private';

export const load: PageServerLoad = async ({ locals }) => {
    const [facilityForm, deleteForm, createFieldForm] = await Promise.all([
        superValidate(zod(facilityCreateSchema), {
            id: 'facility-form',
            defaults: {
                name: '',
                is_primary: false,
                club_id: locals.user?.primary_club_id ?? 0
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
        })
    ]);

    console.log('Load handler - locals:', { user: locals.user, token: !!locals.token });
    
    if (!locals.user?.primary_club_id) {
        return {
            facilityForm,
            deleteForm,
            createFieldForm,
            facilities: [],
            fields: []
        };
    }

        return {
            facilityForm,
            createFieldForm,
            deleteForm,
        };
 
};

export const actions: Actions = {
    create: async ({ request, locals, fetch }) => {
        const form = await superValidate(request, zod(facilityCreateSchema));
        console.log('Form validation result:', form);
        
        const clubId = locals.user?.primary_club_id;
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
            const response = await fetch(`${API_URL}/facilities`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${locals.token}`
                },
                body: JSON.stringify(validatedForm.data)
            });

            const responseData = await response.json();

            if (!response.ok) {
                return fail(response.status, { 
                    form,
                    error: responseData.detail || 'Failed to create facility'
                });
            }
            
            return {
                form,
                facility: responseData
            };
        } catch (err) {
            console.error('Error creating facility:', err);
            return fail(500, { 
                form, 
                error: 'Failed to create facility'
            });
        }
    },

    createField: async ({ request, fetch, locals }) => {
        console.log('CreateField action started');

        // Use superValidate with the request directly to handle JSON data
        const form = await superValidate(request, zod(fieldCreateSchema));

        console.log('Form validation result:', form);
        
        if (!form.valid) {
            console.log('Form validation failed:', form.errors);
            return fail(400, { form });
        }

        try {
            const response = await fetch(`${API_URL}/fields`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${locals.token}`
                },
                body: JSON.stringify(form.data)
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error('Failed to create field:', response.status, errorData);
                return fail(response.status, { 
                    form, 
                    error: errorData.detail || 'Failed to create field'
                });
            }

            const field = await response.json();
            console.log('API Response:', response.status, field);

            return { 
                form,
                success: true,
                field
            };
        } catch (err) {
            console.error('API call failed:', err);
            return fail(500, { 
                form, 
                error: 'Failed to create field' 
            });
        }
    },

    deleteField: async ({ request, fetch, locals }) => {
        const form = await superValidate(request, zod(deleteFieldSchema));

        if (!form.valid) {
            return fail(400, { form });
        }

        try {
            const response = await fetch(`${API_URL}/fields/${form.data.field_id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${locals.token}`
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error('Failed to delete field:', response.status, errorData);
                return fail(response.status, { 
                    form,
                    error: errorData.detail || 'Failed to delete field'
                });
            }

            const result: DeleteFieldResponse = await response.json();
            console.log('DeleteField API Response:', response.status, result);

            return { 
                form,
                success: true,
                message: result.message,
                action: result.action
            };
        } catch (err) {
            console.error('API call failed:', err);
            return fail(500, { 
                form,
                error: 'Failed to delete field' 
            });
        }
    }
} satisfies Actions;
