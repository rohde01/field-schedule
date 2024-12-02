import { redirect } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ cookies, locals }) => {
    cookies.delete('token', { path: '/' });
    locals.user = null;
    throw redirect(303, '/');
};