import type { PageServerLoad, Actions } from './$types';
import { fail, redirect } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms/server';
import { zod } from 'sveltekit-superforms/adapters';
import { createUserSchema } from '$lib/schemas/user';

export const load = (async ({ locals }) => {
	if (locals.user) {
		throw redirect(303, '/dashboard');
	}

	const form = await superValidate(zod(createUserSchema));
	return { form };
}) satisfies PageServerLoad;

export const actions = {
	default: async ({ request, locals }) => {
		const form = await superValidate(request, zod(createUserSchema));
		if (!form.valid) return fail(400, { form });

		const { email, password } = form.data;

		const { error: signUpError } = await locals.supabase.auth.signUp({
			email,
			password
		});

		if (signUpError) {
			return fail(400, {
				form: {
					...form,
					message: signUpError.message ?? 'Registration failed'
				}
			});
		}

		return {
			form,
			confirmationEmailSent: true
		};
	}
} satisfies Actions;
