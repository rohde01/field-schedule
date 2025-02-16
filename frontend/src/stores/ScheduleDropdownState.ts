import type { Schedule } from '$lib/schemas/schedule';
import type { Facility } from '$lib/schemas/facility';
import { writable } from 'svelte/store';

export interface ScheduleDropdownState {
  selectedSchedule: Schedule | null;
  selectedFacility: Facility | null;
  isOpen: boolean;
}

export const dropdownState = writable<ScheduleDropdownState>({
  selectedSchedule: null,
  selectedFacility: null,
  isOpen: false
});

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
