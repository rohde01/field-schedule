import { writable } from 'svelte/store';
import type { Club } from '$lib/schemas/club';

export const clubs = writable<Club[]>([]);

export function setClubs(newClubs: Club[]) {
    clubs.set(newClubs);
}