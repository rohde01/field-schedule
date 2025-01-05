import type { PageServerLoad, Actions } from './$types';
import { fail, redirect } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms/server';
import { zod } from 'sveltekit-superforms/adapters';
import { createUserSchema } from '$lib/schemas/user';
import { API_URL } from '$env/static/private';

export const load = (async ({ locals }) => {
    if (locals.user) {
        throw redirect(303, '/dashboard');
    }
    const form = await superValidate(zod(createUserSchema));
    return { form };
}) satisfies PageServerLoad;

export const actions = {
    default: async ({ request, fetch }) => {
        const form = await superValidate(request, zod(createUserSchema));

        if (!form.valid) {
            return fail(400, { form });
        }

        const response = await fetch(`${API_URL}/users/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(form.data)
        });

        if (!response.ok) {
            const errorData = await response.json();
            return fail(response.status, {
                form: {
                    ...form,
                    message: errorData.detail || 'Registration failed'
                }
            });
        }

        return { form };
    }
} satisfies Actions;


