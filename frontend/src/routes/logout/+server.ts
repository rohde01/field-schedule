import { redirect } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ cookies, locals }) => {
    try {
        cookies.delete('refresh_token', { path: '/' });
        cookies.delete('token', { path: '/' });
        locals.user = null;
    } catch (err) {
        console.error('Error during logout:', err);
    }
    
    throw redirect(303, '/');
};