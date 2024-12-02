import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ cookies, locals }) => {
    try {
        cookies.delete('token', { path: '/' });
        locals.user = null;
        
        return json({ success: true });
    } catch (error) {
        console.error('Logout error:', error);
        return json({ success: false, error: 'Logout failed' }, { status: 500 });
    }
};