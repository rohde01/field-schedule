import type { PageServerLoad, Actions } from './$types';
import { fail, redirect } from '@sveltejs/kit';
import { user } from '$stores/user';
import { superValidate } from 'sveltekit-superforms/server';
import { zod } from 'sveltekit-superforms/adapters';
import { loginSchema } from '$lib/schemas/user';
import type { User } from '$lib/schemas/user';
import { z } from 'zod';

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
                email: form.data.email,
                password: form.data.password,
                grant_type: 'password'
            })
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Login failed:', errorText);
            return fail(response.status, {
                form,
                error: 'Invalid username or password'
            });
        }

        let responseData;
        try {
            responseData = await response.json();
        } catch (error) {
            console.error('Failed to parse response:', error);
            return fail(500, {
                form,
                error: 'Server returned invalid response'
            });
        }

        console.log('Login response data:', responseData);

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

        const userStore: User = {
            user_id: responseData.user.user_id,
            email: responseData.user.email,
            first_name: responseData.user.first_name,
            last_name: responseData.user.last_name,
            role: responseData.user.role,
            primary_club_id: responseData.user.primary_club_id,
        };

        locals.user = userStore;
        user.set(userStore);
        
        throw redirect(303, '/dashboard');
    }
} satisfies Actions;