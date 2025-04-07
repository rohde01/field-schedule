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
export async function createEventOverride(baseEvent: Event, overrideDate: string, activeScheduleId: number) {
    const tempId = -Date.now(); // Temporary negative ID

    // Create optimistic update first
    events.update(eventSchedules => {
        return eventSchedules.map(schedule => ({
            ...schedule,
            entries: [...schedule.entries, {
                ...baseEvent,
                override_id: tempId,
                override_date: overrideDate,
                team_id: baseEvent.team_id,
                field_id: baseEvent.field_id,
                start_time: baseEvent.start_time,
                end_time: baseEvent.end_time,
                week_day: baseEvent.week_day,
                is_deleted: false
            }]
        }));
    });

    // Then persist to server
    const formData = new FormData();
    formData.append('active_schedule_id', String(activeScheduleId));
    formData.append('override_date', overrideDate);
    formData.append('new_start_time', baseEvent.start_time);
    formData.append('new_end_time', baseEvent.end_time);
    formData.append('new_team_id', String(baseEvent.team_id));
    formData.append('new_field_id', String(baseEvent.field_id));
    formData.append('schedule_entry_id', String(baseEvent.schedule_entry_id));

    try {
        const response = await fetch('/dashboard?/createEventOverride', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        const data = JSON.parse(result.data);
        const overrideId = data[data.length - 1];
        
        if (overrideId) {
            console.log('Updating temporary override ID', tempId, 'to permanent ID', overrideId);
            events.update(eventSchedules => {
                return eventSchedules.map(schedule => ({
                    ...schedule,
                    entries: schedule.entries.map(entry => 
                        entry.override_id === tempId 
                            ? { ...entry, override_id: overrideId }
                            : entry
                    )
                }));
            });
        } else {
            console.warn('Invalid response structure:', result);
        }
        
        return result;
    } catch (err) {
        console.error('Failed to create override:', err);
        // Revert optimistic update on error
        events.update(eventSchedules => {
            return eventSchedules.map(schedule => ({
                ...schedule,
                entries: schedule.entries.filter(entry => entry.override_id !== tempId)
            }));
        });
        throw err;
    }
}

// TODO: Implement the deleteEvent function
export function deleteEvent(event: Event, overrideDate?: string): boolean {
    console.warn('Event deletion is not supported');
    return false;
}
