import { writable } from 'svelte/store';
import type { EventSchedule, Event } from '$lib/schemas/event';

export const events = writable<EventSchedule[]>([]);

export function setEvents(newEvents: EventSchedule[]) {
    events.update(() => [...newEvents]);
}

export async function updateEventOverride(eventId: number, overrideId: number, changes: Partial<Event>) {
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

    try {
        const formData = new FormData();
        formData.append('override_id', String(overrideId));
        
        if (changes.start_time) formData.append('new_start_time', changes.start_time);
        if (changes.end_time) formData.append('new_end_time', changes.end_time);
        if (changes.override_date) formData.append('override_date', changes.override_date);
        if ('team_id' in changes) formData.append('new_team_id', changes.team_id !== null ? String(changes.team_id) : '');
        if ('field_id' in changes) formData.append('new_field_id', changes.field_id !== null ? String(changes.field_id) : '');
        if ('is_deleted' in changes) formData.append('is_deleted', String(changes.is_deleted));
        
        const response = await fetch('/dashboard?/updateEventOverride', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to update event override');
        }
        
        return await response.json();
    } catch (err) {
        throw err;
    }
}

export async function createEventOverride(baseEvent: Event, overrideDate: string, activeScheduleId: number) {
    const tempId = -Date.now();

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

    try {
        const formData = new FormData();
        formData.append('active_schedule_id', String(activeScheduleId));
        formData.append('override_date', overrideDate);
        formData.append('new_start_time', baseEvent.start_time);
        formData.append('new_end_time', baseEvent.end_time);
        formData.append('new_team_id', baseEvent.team_id !== null ? String(baseEvent.team_id) : '');
        formData.append('new_field_id', baseEvent.field_id !== null ? String(baseEvent.field_id) : '');
        formData.append('schedule_entry_id', String(baseEvent.schedule_entry_id));

        const response = await fetch('/dashboard?/createEventOverride', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Failed to create event override');
        }
        
        const result = await response.json();
        console.log('Server response:', result);
        
        const parsedData = JSON.parse(result.data);
        const overrideId = parsedData[1];
        
        console.log(`Replacing temp ID ${tempId} with server ID ${overrideId}`);
        
        // Update the temporary ID with the real one
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
        
        return result;
    } catch (err) {
        throw err;
    }
}

export async function deleteEventOverride(overrideId: number) {
    // Update the local store
    events.update(eventSchedules => {
        return eventSchedules.map(schedule => ({
            ...schedule,
            entries: schedule.entries.map(entry => {
                if (entry.override_id === overrideId) {
                    if (entry.schedule_entry_id) {
                        // Mark as deleted if it has a schedule_entry_id
                        return { ...entry, is_deleted: true };
                    }
                    // Return null to be filtered out if no schedule_entry_id
                    return null;
                }
                return entry;
            }).filter((entry): entry is Event => entry !== null)
        }));
    });

    try {
        const formData = new FormData();
        formData.append('override_id', String(overrideId));
        
        const response = await fetch('/dashboard?/deleteEventOverride', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to delete event override');
        }
        
        return await response.json();
    } catch (err) {
        console.error('Error deleting event override:', err);
        throw err;
    }
}
