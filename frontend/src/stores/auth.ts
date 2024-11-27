import { writable, type Writable, get } from 'svelte/store';
import { browser } from '$app/environment';

interface User {
    username: string;
    email: string;
    role: string;
    [key: string]: any;
}

const storedToken: string | null = browser ? localStorage.getItem('token') : null;
const storedUser: User | null = browser ? JSON.parse(localStorage.getItem('user') ?? 'null') : null;

export const token: Writable<string | null> = writable(storedToken);
export const user: Writable<User | null> = writable(storedUser);

// Subscribe to changes and update localStorage
if (browser) {
    token.subscribe((value: string | null) => {
        if (value) localStorage.setItem('token', value);
        else localStorage.removeItem('token');
    });

    user.subscribe((value: User | null) => {
        if (value) localStorage.setItem('user', JSON.stringify(value));
        else localStorage.removeItem('user');
    });
}

export function logout(): void {
    token.set(null);
    user.set(null);
}

export function isAuthenticated(): boolean {
    return !!get(token);
}