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

// This function creates an override for an existing base event
export function createEventOverride(baseEvent: Event, overrideDate: string) {
    events.update(eventSchedules => {
        return eventSchedules.map(schedule => ({
            ...schedule,
            entries: [...schedule.entries, {
                ...baseEvent,
                override_id: -Date.now(),
                override_date: overrideDate
            }]
        }));
    });
}


// TODO: Implement the deleteEvent function
export function deleteEvent(event: Event, overrideDate?: string): boolean {
    console.warn('Event deletion is not supported');
    return false;
}
