import { get } from 'svelte/store';
import { token, user } from '../stores/auth';
import { goto } from '$app/navigation';

interface ApiOptions extends RequestInit {
    headers?: Record<string, string>;
}

export async function apiFetch(endpoint: string, options: ApiOptions = {}): Promise<Response> {
    const authToken = get(token);
    const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        ...(authToken ? { 'Authorization': `Bearer ${authToken}` } : {}),
        ...(options.headers || {})
    };

    const response = await fetch(`http://localhost:8000${endpoint}`, {
        ...options,
        headers
    });

    if (response.status === 401) {
        token.set(null);
        user.set(null);
        goto('/login');
    }

    return response;
}