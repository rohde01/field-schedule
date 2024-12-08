import { writable } from 'svelte/store';
import type { User } from '$lib/types/user';

export const user = writable<User | null>(null);

user.subscribe((value) => {
    console.log('User store updated:', value);
});