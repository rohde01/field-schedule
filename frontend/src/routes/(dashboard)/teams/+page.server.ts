import { fail } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms/server';
import { zod } from 'sveltekit-superforms/adapters';
import { teamSchema, deleteTeamSchema, updateTeamSchema, type DeleteTeamResponse, type UpdateTeamResponse } from '$lib/schemas/team';
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
    
    const updateForm = await superValidate(zod(updateTeamSchema), {
        id: 'update-team-form',
    });
    
    if (!locals.user?.club_id) {
        return {
            deleteForm,
            createForm,
            updateForm,
            teams: []
        };
    }

    return {
        deleteForm,
        createForm,
        updateForm,
    };
})

export const actions: Actions = {
    create: async ({ request, locals: { supabase, user } }) => {
        if (!user?.club_id) {
            const form = await superValidate(request, zod(teamSchema));
            return fail(400, { 
                form, 
                message: 'No club ID set for user' 
            });
        }

        const formData = await request.formData();
        formData.set('club_id', user.club_id.toString());
        formData.set('is_active', 'true');
        
        const form = await superValidate(formData, zod(teamSchema));
        
        if (!form.valid) {
            return fail(400, { 
                form
            });
        }

        try {
            const { data: team, error: insertError } = await supabase
                .from('teams')
                .insert(form.data)
                .select()
                .single();

            if (insertError) {
                form.message = insertError.message || 'Failed to create team';
                return fail(400, { form });
            }

            form.message = 'Team created successfully';
            return { 
                form,
                success: true,
                team
            };
        } catch (err) {
            form.message = 'Failed to create team';
            return fail(500, { form });
        }
    },

    update: async ({ request, locals: { supabase, user } }) => {
        if (!user?.club_id) {
            const form = await superValidate(request, zod(updateTeamSchema));
            form.message = 'No club ID set for user';
            return fail(400, { form });
        }

        const formData = await request.formData();
        formData.set('club_id', user.club_id.toString());
        
        const form = await superValidate(formData, zod(updateTeamSchema));
        
        if (!form.valid) {
            return fail(400, { form });
        }

        try {
            const { data: team, error: updateError } = await supabase
                .from('teams')
                .update(form.data)
                .eq('team_id', form.data.team_id)
                .select()
                .single();

            if (updateError) {
                form.message = updateError.message || 'Failed to update team';
                return fail(400, { form });
            }

            form.message = 'Team updated successfully';
            return { 
                form,
                success: true,
                team,
                action: 'update'
            };
        } catch (err) {
            form.message = 'Failed to update team';
            return fail(500, { form });
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
                form.message = deleteError.message || 'Failed to delete team';
                return fail(400, { form });
            }

            form.message = 'Team deleted successfully';
            return { 
                form,
                success: true,
                action: 'delete'
            };
        } catch (err) {
            form.message = 'Failed to delete team';
            return fail(500, { form });
        }
    }
};