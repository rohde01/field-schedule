import { fail } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms/server';
import { zod } from 'sveltekit-superforms/adapters';
import { teamSchema, deleteTeamSchema, type DeleteTeamResponse } from '$lib/schemas/team';
import type { PageServerLoad, Actions } from './$types';
import { API_URL } from '$env/static/private';

export const load = (async ({ locals }) => {
    const deleteForm = await superValidate(zod(deleteTeamSchema));
    const createForm = await superValidate(zod(teamSchema), {
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
            is_active: true,
            weekly_trainings: 1
        }
    });
    
    if (!locals.user?.primary_club_id) {
        console.log('No primary_club_id found');
        return {
            deleteForm,
            createForm,
            teams: []
        };
    }

    return {
        deleteForm,
        createForm,
    };
}) satisfies PageServerLoad;

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
            const response = await fetch(`${API_URL}/teams`, {
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

            const team = await response.json();
            console.log('API Response:', response.status, team);

            return { 
                form,
                success: true,
                team
            };
        } catch (err) {
            console.error('API call failed:', err);
            return fail(500, { 
                form, 
                error: 'Failed to create team' 
            });
        }
    },

    deleteTeam: async ({ request, fetch, locals }) => {
        const form = await superValidate(request, zod(deleteTeamSchema));

        if (!form.valid) {
            return fail(400, { form });
        }

        try {
            const response = await fetch(`${API_URL}/teams/${form.data.team_id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${locals.token}`
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                return fail(response.status, { 
                    form,
                    error: errorData.detail || 'Failed to delete team'
                });
            }

            const result: DeleteTeamResponse = await response.json();
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
                error: 'Failed to delete team' 
            });
        }
    }
};