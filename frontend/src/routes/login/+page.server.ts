import type { PageServerLoad } from './$types';
import { fail, redirect } from '@sveltejs/kit';
import type { Actions } from './$types';

export const load = (async () => {
    return {};
}) satisfies PageServerLoad;

export const actions: Actions = {
    default: async ({ request, cookies }) => {
        const data = await request.formData();
        const username = data.get('username');
        const password = data.get('password');

        if (!username || !password) {
            return fail(400, { 
                error: 'Missing username or password',
                username: username?.toString()
            });
        }

        const response = await fetch('http://localhost:8000/users/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({
                username: username.toString(),
                password: password.toString()
            })
        });

        const responseData = await response.json();

        if (!response.ok) {
            return fail(response.status, {
                error: 'Invalid username or password',
                username: username.toString()
            });
        }

        cookies.set('token', responseData.access_token, {
            path: '/',
            httpOnly: true,
            sameSite: 'strict',
            secure: process.env.NODE_ENV === 'production',
            maxAge: 60 * 60 * 24 // 1 day
        });

        return {
            userData: {
                id: responseData.user_id,
                firstName: responseData.first_name,
                lastName: responseData.last_name,
                email: responseData.email,
                role: responseData.role
            }
        };
    }
};