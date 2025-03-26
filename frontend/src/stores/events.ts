import { writable } from 'svelte/store';
import type { EventSchedule } from '$lib/schemas/event';

export const events = writable<EventSchedule[]>([]);

export function setEvents(newEvents: EventSchedule[]) {
    events.update(() => {
        console.log('Setting events to:', newEvents);
        return [...newEvents];
    });
}
