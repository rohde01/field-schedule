import { createSupabaseServerClient } from '@supabase/auth-helpers-sveltekit';
import { PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_ANON_KEY } from '$env/static/public';
import type { Handle } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
	const supabase = createSupabaseServerClient({
		supabaseUrl: PUBLIC_SUPABASE_URL,
		supabaseKey: PUBLIC_SUPABASE_ANON_KEY,
		event,
		cookieOptions: {
			secure: process.env.NODE_ENV === 'production'
		}
	});

	event.locals.supabase = supabase;

	const {
		data: { session }
	} = await supabase.auth.getSession();

	event.locals.user = session?.user ?? null;
	event.locals.token = session?.access_token ?? null;

	return resolve(event);
};
