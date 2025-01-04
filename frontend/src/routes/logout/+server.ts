import { redirect } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { user } from '../../stores/user';

export const POST: RequestHandler = async ({ cookies, locals }) => {
    try {
        user.set(null);
        cookies.delete('refresh_token', { path: '/' });
        cookies.delete('token', { path: '/' });
        locals.user = null;
    } catch (err) {
        console.error('Error during logout:', err);
    }
    
    throw redirect(303, '/');
};