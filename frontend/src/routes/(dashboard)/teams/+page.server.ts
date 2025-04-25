import { fail } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms/server';
import { zod } from 'sveltekit-superforms/adapters';
import { teamSchema, deleteTeamSchema, type DeleteTeamResponse } from '$lib/schemas/team';
import type { Actions } from './$types';

// Disable SSR for this route to prevent circular dependency issues
export const ssr = false;

export const load = (async ({ locals }) => {
    const deleteForm = await superValidate(zod(deleteTeamSchema), { id: 'delete-team-form' });
    const createForm = await superValidate(zod(teamSchema), {
        id: 'team-form',
        defaults: {
            name: '',
            year: '',
            club_id: locals.user?.club_id ?? 0,
            gender: 'boys',
            is_academy: false,
            minimum_field_size: 125,
            preferred_field_size: null,
            level: 1,
            is_active: true,
            weekly_trainings: 1
        }
    });
    
    if (!locals.user?.club_id) {
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
})

export const actions: Actions = {
    create: async ({ request, locals: { supabase, user } }) => {
        if (!user?.club_id) {
            const form = await superValidate(request, zod(teamSchema));
            return fail(400, { 
                form, 
                error: 'No club ID set for user' 
            });
        }

        const formData = await request.formData();
        formData.set('club_id', user.club_id.toString());
        formData.set('is_active', 'true');
        
        const form = await superValidate(formData, zod(teamSchema));
        
        if (!form.valid) {
            return fail(400, { form });
        }

        try {
            const { data: team, error: insertError } = await supabase
                .from('teams')
                .insert(form.data)
                .select()
                .single();

            if (insertError) {
                return fail(400, { 
                    form, 
                    error: insertError.message || 'Failed to create team'
                });
            }

            return { 
                form,
                success: true,
                team
            };
        } catch (err) {
            return fail(500, { 
                form, 
                error: 'Failed to create team' 
            });
        }
    },

    deleteTeam: async ({ request, locals: { supabase } }) => {
        const form = await superValidate(request, zod(deleteTeamSchema));

        if (!form.valid) {
            return fail(400, { form });
        }

        try {
            const { error: deleteError } = await supabase
                .from('teams')
                .delete()
                .eq('team_id', form.data.team_id);

            if (deleteError) {
                return fail(400, { 
                    form,
                    error: deleteError.message || 'Failed to delete team'
                });
            }

            const result: DeleteTeamResponse = {
                message: 'Team deleted successfully',
                action: 'delete'
            };

            return { 
                form,
                success: true,
                message: result.message,
                action: result.action
            };
        } catch (err) {
            return fail(500, { 
                form,
                error: 'Failed to delete team' 
            });
        }
    }
};