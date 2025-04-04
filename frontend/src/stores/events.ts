import { writable, get } from 'svelte/store';
import type { EventSchedule, Event } from '$lib/schemas/event';

export const events = writable<EventSchedule[]>([]);

export function setEvents(newEvents: EventSchedule[]) {
    events.update(() => {
        console.log('Setting events to:', newEvents);
        return [...newEvents];
    });
}

export function updateEventOverride(eventId: number, overrideId: number, changes: Partial<Event>) {
    events.update(eventSchedules => {
        const updatedEventSchedules = eventSchedules.map(schedule => {
            const updatedEntries = schedule.entries.map(entry => {
                if (entry.schedule_entry_id === eventId && entry.override_id === overrideId) {
                    return { ...entry, ...changes };
                }
                return entry;
            });
            return { ...schedule, entries: updatedEntries };
        });
        return updatedEventSchedules;
    });
}
