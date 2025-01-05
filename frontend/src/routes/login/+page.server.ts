import type { PageServerLoad, Actions } from './$types';
import { fail, redirect } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms/server';
import { zod } from 'sveltekit-superforms/adapters';
import { loginSchema } from '$lib/schemas/user';
import type { LoginResponse } from '$lib/schemas/user';

export const load = (async ({ locals }) => {
    if (locals.user) {
        throw redirect(303, '/dashboard');
    }
    const form = await superValidate(zod(loginSchema));
    return { form };
}) satisfies PageServerLoad;


export const actions = {
    default: async ({ request, cookies, locals }) => {
        const form = await superValidate(request, zod(loginSchema));

        if (!form.valid) {
            return fail(400, { form });
        }

        const response = await fetch('http://localhost:8000/users/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            },
            body: new URLSearchParams({
                username: form.data.email,
                password: form.data.password,
                grant_type: 'password'
            })
        });

        if (!response.ok) {
            const errorText = await response.text();
            let errorMessage = 'Oops! Invalid email or password';
            try {
                const errorJson = JSON.parse(errorText);
                errorMessage = errorJson.detail || errorMessage;
            } catch {
                // Use default message if parsing fails
            }
            return fail(response.status, {
                form: {
                    ...form,
                    message: errorMessage
                }
            });
        }

        let responseData;
        try {
            responseData = await response.json() as LoginResponse;
        } catch (error) {
            return fail(500, {
                form,
                message: 'Server returned invalid response'
            });
        }

        // Set access token cookie
        cookies.set('token', responseData.access_token, {
            path: '/',
            httpOnly: true,
            sameSite: 'strict',
            secure: process.env.NODE_ENV === 'production',
            maxAge: 60 * 30 // 30 minutes
        });

        // Set refresh token cookie
        cookies.set('refresh_token', responseData.refresh_token, {
            path: '/',
            httpOnly: true,
            sameSite: 'strict',
            secure: process.env.NODE_ENV === 'production',
            maxAge: 60 * 60 * 24 * 7 // 7 days
        });

        // Set user data in locals
        locals.user = responseData.user;
        
        throw redirect(303, '/dashboard');
    }
} satisfies Actions;