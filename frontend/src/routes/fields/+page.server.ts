import type { PageServerLoad, Actions } from './$types';
import { error, fail } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms/server';
import { zod } from 'sveltekit-superforms/adapters';
import type { Facility } from '$lib/schemas/facility';
import { facilityCreateSchema } from '$lib/schemas/facility';
import { deleteFieldSchema, fieldCreateSchema, type DeleteFieldResponse } from '$lib/schemas/field';
import type { Field } from '$lib/schemas/field';

export const load: PageServerLoad = async ({ locals, fetch }) => {
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
        console.log('No primary_club_id found');
        return {
            facilityForm,
            deleteForm,
            createFieldForm,
            facilities: [],
            fields: []
        };
    }

    try {
        const [facilitiesResponse, fieldsResponse] = await Promise.all([
            fetch(`http://localhost:8000/facilities/club/${locals.user.primary_club_id}`, {
                headers: {
                    'Authorization': `Bearer ${locals.token}`
                }
            }),
            fetch(`http://localhost:8000/fields/club/${locals.user.primary_club_id}`, {
                headers: {
                    'Authorization': `Bearer ${locals.token}`
                }
            })
        ]);

        if (!facilitiesResponse.ok) {
            const errorText = await facilitiesResponse.text();
            console.error('Failed to fetch facilities:', facilitiesResponse.status, errorText);
            throw error(facilitiesResponse.status, 'Failed to fetch facilities');
        }

        if (!fieldsResponse.ok) {
            const errorText = await fieldsResponse.text();
            console.error('Failed to fetch fields:', fieldsResponse.status, errorText);
            throw error(fieldsResponse.status, 'Failed to fetch fields');
        }

        const facilities: Facility[] = await facilitiesResponse.json();
        const fields: Field[] = await fieldsResponse.json();
        
        console.log('Fetched facilities:', facilities);
        console.log('Fetched fields:', fields);

        return {
            facilityForm,
            createFieldForm,
            deleteForm,
            facilities,
            fields,
        };
    } catch (err) {
        console.error('Error in load function:', err);
        throw error(500, 'Internal Server Error');
    }
};

export const actions: Actions = {
    create: async ({ request, locals, fetch }) => {
        const form = await superValidate(request, zod(facilityCreateSchema));
        console.log('Form validation result:', form);
        
        if (!form.valid) {
            return fail(400, { form });
        }

        const clubId = locals.user?.primary_club_id;
        if (!clubId) {
            return fail(400, { 
                form,
                error: 'No club ID found for user'
            });
        }

        form.data.club_id = clubId;

        try {
            const response = await fetch('http://localhost:8000/facilities', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${locals.token}`
                },
                body: JSON.stringify(form.data)
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
            const response = await fetch('http://localhost:8000/fields', {
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
            const response = await fetch(`http://localhost:8000/fields/${form.data.field_id}`, {
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
