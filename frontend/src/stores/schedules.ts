import { writable, get } from 'svelte/store';
import type { Schedule, ScheduleEntry } from '$lib/schemas/schedule';
import { selectSchedule, dropdownState } from './ScheduleDropdownState';

export const schedules = writable<Schedule[]>([]);

schedules.subscribe((schedulesList) => {
    if (schedulesList.length === 0) return;

    const currentDropdown = get(dropdownState);
    if (currentDropdown.selectedSchedule) {
        const currentId = currentDropdown.selectedSchedule.schedule_id;
        const updatedSchedule = schedulesList.find(s => s.schedule_id === currentId);
        if (updatedSchedule) {
            selectSchedule(updatedSchedule);
        } else {
            selectSchedule(schedulesList[schedulesList.length - 1]);
        }
    } else {
        selectSchedule(schedulesList[schedulesList.length - 1]);
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
