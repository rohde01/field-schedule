import { fail, redirect } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms/server';
import { zod } from 'sveltekit-superforms/adapters';
import { updateNameSchema } from '$lib/schemas/user';
import type { Actions, PageServerLoad } from './$types';

export const load = (async ({ locals: { supabase, user } }) => {
    if (user?.first_name && user?.last_name) {
        throw redirect(303, '/dashboard');
    }

    const form = await superValidate(zod(updateNameSchema));
    return { form };
}) satisfies PageServerLoad;

export const actions: Actions = {
    default: async ({ request, locals: { supabase, user } }) => {
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

        const { error, data } = await supabase
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

        throw redirect(303, '/dashboard');
    }
};