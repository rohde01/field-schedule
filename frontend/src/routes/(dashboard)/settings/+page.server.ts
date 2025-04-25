import { fail, redirect } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms/server';
import { zod } from 'sveltekit-superforms/adapters';
import { updateNameSchema } from '$lib/schemas/user';
import { createClubSchema } from '$lib/schemas/club';
import type { Actions, PageServerLoad } from './$types';

export const load = (async ({ locals: { supabase, user } }) => {
    if (user?.first_name && user?.last_name && user?.club_id) {
        throw redirect(303, '/schedules');
    }

    const nameForm = await superValidate(zod(updateNameSchema));
    const clubForm = await superValidate(zod(createClubSchema));
    
    return { 
        nameForm,
        clubForm,
        user,
        supabase
    };
}) satisfies PageServerLoad;

export const actions: Actions = {
    updateName: async ({ request, locals: { supabase, user } }) => {
        const form = await superValidate(request, zod(updateNameSchema));

        if (!form.valid) {
            return fail(400, { form });
        }

        if (!user) {
            return fail(401, {
                form: {
                    ...form,
                    message: 'User not authenticated'
                }
            });
        }

        const { first_name, last_name } = form.data;

        const { error } = await supabase
            .from('users')
            .update({ first_name, last_name })
            .eq('user_id', user.user_id)
            .select()
            .single();

        if (error) {
            return fail(400, {
                form: {
                    ...form,
                    message: 'Failed to update profile'
                }
            });
        }

        throw redirect(303, '/schedules');
    },

    createClub: async ({ request, locals: { supabase, user } }) => {
        const form = await superValidate(request, zod(createClubSchema));

        if (!form.valid) {
            return fail(400, { form });
        }

        if (!user) {
            return fail(401, {
                form: {
                    ...form,
                    message: 'User not authenticated'
                }
            });
        }

        // Create the club with owner_id
        const { error: clubError, data: clubData } = await supabase
            .from('clubs')
            .insert({ 
                name: form.data.name,
                owner_id: user.user_id
            })
            .select()
            .single();

        if (clubError) {
            return fail(400, {
                form: {
                    ...form,
                    message: `Failed to create club: ${clubError.message}`
                }
            });
        }

        // Update user with club_id
        const { error: userError } = await supabase
            .from('users')
            .update({ club_id: clubData.club_id })
            .eq('user_id', user.user_id);

        if (userError) {
            return fail(400, {
                form: {
                    ...form,
                    message: `Failed to update user club: ${userError.message}`
                }
            });
        }

        throw redirect(303, '/schedules');
    }
};