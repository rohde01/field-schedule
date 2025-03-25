import { writable } from 'svelte/store';
import type { Event } from '$lib/schemas/event';

export const events = writable<Event[]>([]);

export function setEvents(newEvents: Event[]) {
    events.update(() => {
        console.log('Setting events to:', newEvents);
        return [...newEvents];
    });
}
