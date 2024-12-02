import type { PageServerLoad, Actions } from './$types';
import { fail, redirect } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ locals }) => {
    if (locals.user) {
        throw redirect(303, '/dashboard');
    }
    return {};
};

export const actions: Actions = {
    default: async ({ request, cookies, locals }) => {
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

        const userData = {
            id: responseData.user_id,
            firstName: responseData.first_name,
            lastName: responseData.last_name,
            email: responseData.email,
            role: responseData.role
        };

        locals.user = userData;
        console.log('User data in locals:', locals.user);
        
        throw redirect(303, '/dashboard');
    }
};