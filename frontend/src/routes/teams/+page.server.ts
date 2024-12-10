import { fail } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms/server';
import { teamSchema } from '$lib/schemas/team';
import type { PageServerLoad, Actions } from './$types';
import { zod } from 'sveltekit-superforms/adapters';
import type { TeamSchema } from '$lib/schemas/team';
import { error } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ fetch, locals }) => {
    const form = await superValidate(zod(teamSchema), {
        id: 'team-form',
        defaults: {
            name: '',
            year: '',
            club_id: locals.user?.primary_club_id ?? 0,
            gender: 'boys',
            is_academy: false,
            minimum_field_size: 125,
            preferred_field_size: null,
            level: 1,
            is_active: true
        }
    });

    console.log('Load handler - locals:', { user: locals.user, token: !!locals.token });
    
    if (!locals.user?.primary_club_id) {
        console.log('No primary_club_id found');
        return {
            form,
            teams: []
        };
    }

    const response = await fetch(`http://localhost:8000/teams?club_id=${locals.user.primary_club_id}`, {
        headers: {
            'Authorization': `Bearer ${locals.token}`
        }
    });

    if (!response.ok) {
        console.error('Failed to fetch teams:', response.status, await response.text());
        throw error(response.status, 'Failed to fetch teams');
    }

    const teams = await response.json() as TeamSchema[];
    console.log('Fetched teams:', teams);

    return {
        form,
        teams
    };
};

export const actions: Actions = {
    create: async ({ request, fetch, locals }) => {
        console.log('Create action started');
        
        if (!locals.user?.primary_club_id) {
            console.log('No primary club ID found');
            const form = await superValidate(request, zod(teamSchema));
            return fail(400, { 
                form, 
                error: 'No primary club ID set for user' 
            });
        }

        const formData = await request.formData();
        formData.set('club_id', locals.user.primary_club_id.toString());
        formData.set('is_active', 'true');
        
        const form = await superValidate(formData, zod(teamSchema));
        console.log('Form validation result:', form);
        
        if (!form.valid) {
            console.log('Form validation failed:', form.errors);
            return fail(400, { form });
        }

        console.log('Sending team data:', form.data);

        try {
            const response = await fetch('http://localhost:8000/teams', {
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
                    error: errorData.detail || 'Failed to create team'
                });
            }

            const responseText = await response.text();
            console.log('API Response:', response.status, responseText);

            if (!response.ok) {
                return fail(response.status, { 
                    form, 
                    error: responseText 
                });
            }

            return { 
                form,
                success: true 
            };
        } catch (err) {
            console.error('API call failed:', err);
            return fail(500, { 
                form, 
                error: 'Failed to create team' 
            });
        }
    }
};