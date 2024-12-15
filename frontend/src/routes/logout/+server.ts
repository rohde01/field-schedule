import { redirect } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { user } from '../../stores/user';

export const POST: RequestHandler = async ({ cookies, locals }) => {
    user.set(null);

    cookies.delete('token', { path: '/' });
    locals.user = null;
    throw redirect(303, '/');
};