import { writable } from 'svelte/store';
import type { Schedule, ScheduleEntry } from '$lib/schemas/schedule';
import { selectSchedule } from './ScheduleDropdownState';

export const schedules = writable<Schedule[]>([]);

schedules.subscribe((schedulesList) => {
    if (schedulesList.length > 0) {
        const lastSchedule = schedulesList[schedulesList.length - 1];
        selectSchedule(lastSchedule);
    }
});

export function setSchedules(newSchedules: Schedule[]) {
    schedules.update(() => {
        console.log('Setting schedules to:', newSchedules);
        return [...newSchedules];
    });
}

export function addSchedule(schedule: Schedule) {
    schedules.update(schedules => {
        const updatedSchedules = [...schedules, schedule];
        console.log('Updated schedules after adding:', updatedSchedules);
        return updatedSchedules;
    });
}

export function updateScheduleEntry(entryId: number, changes: Partial<ScheduleEntry>) {
    schedules.update(schedulesList => {
        return schedulesList.map(schedule => {
            const updatedEntries = schedule.entries.map(entry => {
                if (entry.schedule_entry_id === entryId) {
                    return { ...entry, ...changes };
                }
                return entry;
            });
            return { ...schedule, entries: updatedEntries };
        });
    });
}
