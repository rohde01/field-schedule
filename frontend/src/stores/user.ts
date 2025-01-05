import { writable } from 'svelte/store';
import type { User } from '$lib/schemas/user';

export const user = writable<User | null>(null);