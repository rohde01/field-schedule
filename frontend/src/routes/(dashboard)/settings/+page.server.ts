import { fail, redirect } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms/server';
import { zod } from 'sveltekit-superforms/adapters';
import { updateUserSchema } from '$lib/schemas/user';
import { createClubSchema } from '$lib/schemas/club';
import type { Actions, PageServerLoad } from './$types';

export const ssr = false

export const load = (async ({ locals: { user } }) => {
    // Prefill user form with current user details
    const userForm = await superValidate(
      { email: user?.email, first_name: user?.first_name, last_name: user?.last_name, role: user?.role },
      zod(updateUserSchema)
    );
    const clubForm = await superValidate(zod(createClubSchema));
    
    return { 
        userForm,
        clubForm,
        user,
        hasClub: Boolean(user?.club_id)
    };
}) satisfies PageServerLoad;

export const actions: Actions = {
    updateUser: async ({ request, locals: { supabase, user } }) => {
        const form = await superValidate(request, zod(updateUserSchema));

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

        const { error } = await supabase
            .from('users')
            .update({ ...form.data })
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

        // Set success message and return form
        form.message = 'Profile updated successfully';
        return { form };
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