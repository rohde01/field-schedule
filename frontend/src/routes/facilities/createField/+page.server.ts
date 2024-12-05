import type { PageServerLoad, Actions } from './$types';
import { fail } from '@sveltejs/kit';
import type { Field, CreateFieldResponse } from '$lib/types/field';

export const load = (async () => {
    return {};
}) satisfies PageServerLoad;

export const actions = {
    createField: async ({ request, fetch }) => {
        const formData = await request.formData();
        
        try {
            const fieldData = JSON.parse(formData.get('fieldData') as string);
            console.log('Sending field data:', fieldData); // Debug log

            const response = await fetch('http://localhost:8000/fields', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(fieldData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error('Server error:', errorData);
                return fail(response.status, { 
                    error: errorData.detail || 'Failed to create field' 
                });
            }

            const result: CreateFieldResponse = await response.json();
            return { success: true, field_id: result.field_id };

        } catch (error) {
            console.error('Error creating field:', error);
            return fail(500, { 
                error: 'Failed to create field' 
            });
        }
    }
} satisfies Actions;