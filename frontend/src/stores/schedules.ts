import { writable, derived } from 'svelte/store';
import type { Schedule } from '$lib/schemas/schedule';
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
