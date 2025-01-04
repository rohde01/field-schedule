import type { PageServerLoad, Actions } from './$types';
import { fail, redirect } from '@sveltejs/kit';
import { user } from '$stores/user';

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
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            },
            body: new URLSearchParams({
                username: username.toString(),
                password: password.toString(),
                grant_type: 'password'
            })
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Login failed:', errorText);
            return fail(response.status, {
                error: 'Invalid username or password',
                username: username.toString()
            });
        }

        let responseData;
        try {
            responseData = await response.json();
        } catch (error) {
            console.error('Failed to parse response:', error);
            return fail(500, {
                error: 'Server returned invalid response',
                username: username.toString()
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

             const userStore = {
            id: responseData.user.user_id,
            firstName: responseData.user.first_name,
            lastName: responseData.user.last_name,
            email: responseData.user.email,
            role: responseData.user.role,
            primary_club_id: responseData.primary_club_id,
        };

        locals.user = userStore;
        user.set(userStore);
        
        throw redirect(303, '/dashboard');
    }
};