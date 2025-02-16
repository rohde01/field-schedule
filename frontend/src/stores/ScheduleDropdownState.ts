import type { Schedule } from '$lib/schemas/schedule';
import { writable } from 'svelte/store';

type ScheduleDropdownState = {
    isOpen: boolean;
    selectedSchedule: Schedule | null;
};

const initialState: ScheduleDropdownState = {
    isOpen: false,
    selectedSchedule: null,
};

export const dropdownState = writable<ScheduleDropdownState>(initialState);

export function toggleDropdown(key: keyof Pick<ScheduleDropdownState, 'isOpen'>) {
    dropdownState.update(state => ({
        ...state,
        [key]: !state[key]
    }));
}

export function selectSchedule(schedule: Schedule | null) {
    import('./ScheduleSidebarState').then(({ SidebarDropdownState }) => {
        if (!schedule || schedule.schedule_id >= 0) {
            SidebarDropdownState.update(state => ({
                ...state,
                showCreateSchedule: false
            }));
        }
    });

    dropdownState.update(state => ({
        ...state,
        selectedSchedule: schedule
    }));
}

export function selectAndShowSchedule(schedule: Schedule | null) {
    dropdownState.update(state => {
        const newState = {
            ...state,
            selectedSchedule: schedule,
            isOpen: false
        };
        return newState;
    });
}
