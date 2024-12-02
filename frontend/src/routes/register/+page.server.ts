import type { PageServerLoad } from './$types';
import { redirect, fail } from '@sveltejs/kit';
import type { RequestEvent } from '@sveltejs/kit';

export const load = (async () => {
    return {};
}) satisfies PageServerLoad;

export const actions = {
    default: async ({request}: RequestEvent) => {
        const data = await request.formData();
        const username = data.get('username');
        const password = data.get('password');
        const first_name = data.get('first_name');
        const last_name = data.get('last_name');
        const email = data.get('email');

        if (!username || !password || !first_name || !last_name || !email) {
            return fail(400, {
                error: 'Missing required fields',
                username: username?.toString(),
                firstName: first_name?.toString(),
                lastName: last_name?.toString(),
                email: email?.toString()
            });
        }

        const response = await fetch('http://localhost:8000/users/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username.toString(),
                password: password.toString(),
                first_name: first_name.toString(),
                last_name: last_name.toString(),
                email: email.toString()
            })
        });

        const responseData = await response.json();

        if (!response.ok) {
            return fail(response.status, {
                error: responseData.detail || 'Registration failed',
                username: username.toString(),
                firstName: first_name.toString(),
                lastName: last_name.toString(),
                email: email.toString()
            });
        }
        
        return redirect(303, '/login');
    }
};


