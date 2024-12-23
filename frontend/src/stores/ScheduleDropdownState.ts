import type { Schedule } from '$lib/schemas/schedule';
import { writable } from 'svelte/store';
import { schedules } from './schedules';

type ScheduleDropdownState = {
    isOpen: boolean;
    selectedSchedule: Schedule | null;
};

const initialState: ScheduleDropdownState = {
    isOpen: false,
    selectedSchedule: null
};

export const dropdownState = writable<ScheduleDropdownState>(initialState);


dropdownState.subscribe(state => {
    if (state.selectedSchedule) {
        console.log('Selected schedule changed:', state.selectedSchedule);
    }
});

export function toggleDropdown(key: keyof Pick<ScheduleDropdownState, 'isOpen'>) {
    dropdownState.update(state => ({
        ...state,
        [key]: !state[key]
    }));
}

export function selectSchedule(schedule: Schedule) {
    dropdownState.update(state => ({
        ...state,
        selectedSchedule: schedule,
    }));
}
