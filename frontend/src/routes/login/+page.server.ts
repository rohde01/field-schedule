import type { PageServerLoad, Actions } from './$types';
import { fail, redirect } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms/server';
import { zod } from 'sveltekit-superforms/adapters';
import { loginSchema } from '$lib/schemas/user';

export const load = (async ({ locals }) => {
	if (locals.user) {
		throw redirect(303, '/dashboard');
	}
	const form = await superValidate(zod(loginSchema));
	return { form };
}) satisfies PageServerLoad;

export const actions = {
	default: async ({ request, locals }) => {
		const form = await superValidate(request, zod(loginSchema));
		if (!form.valid) return fail(400, { form });

		const { email, password } = form.data;

		const { data, error } = await locals.supabase.auth.signInWithPassword({ email, password });

		if (error || !data.session || !data.user) {
			return fail(400, {
				form: {
					...form,
					message: error?.message ?? 'Invalid email or password'
				}
			});
		}

		// Session cookie is automatically handled by Supabase server helpers
		// `locals.user` is now set in the next request

		throw redirect(303, '/dashboard');
	}
} satisfies Actions;
