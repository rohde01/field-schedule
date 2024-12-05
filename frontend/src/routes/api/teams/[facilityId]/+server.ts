import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ params, locals, fetch }) => {
    if (!locals.user) {
        return new Response('Unauthorized', { status: 401 });
    }

    const fieldsResponse = await fetch(`http://localhost:8000/fields/facility/${params.facilityId}`);
    
    if (!fieldsResponse.ok) {
        if (fieldsResponse.status !== 404) {
            return new Response('Failed to fetch fields', { status: fieldsResponse.status });
        }
        return json([]);
    }

    const fields = await fieldsResponse.json();
    return json(fields);
};
