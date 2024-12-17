import { writable } from 'svelte/store';
import type { Schedule } from '$lib/schemas/schedule';

export const schedules = writable([] as Schedule[]);

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
