import { writable } from 'svelte/store';
import type { Team } from '$lib/schemas/team';
import { dropdownState } from './ScheduleDropdownState';

type SidebarDropdownState = {
    teamsOpen: boolean;
    selectedTeam: Team | null;
    showCreateSchedule: boolean;
};

const initialState: SidebarDropdownState = {
    teamsOpen: true,
    selectedTeam: null,
    showCreateSchedule: false
};

const store = writable<SidebarDropdownState>(initialState);
export const SidebarDropdownState = store;

export function toggleDropdown(key: keyof Pick<SidebarDropdownState, 'teamsOpen'>) {
    SidebarDropdownState.update(state => {
        const newState = {
            ...state,
            [key]: !state[key]
        };
        return newState;
    });
}

export function selectTeam(team: Team) {
    SidebarDropdownState.update(state => {
        const newState = {
            ...state,
            selectedTeam: team,
            showCreateTeam: false
        };
        return newState;
    });
}

export function toggleCreateSchedule() {
    SidebarDropdownState.update(state => {
        const newState = {
            ...state,
            showCreateSchedule: !state.showCreateSchedule,
        };
        return newState;
    });
    dropdownState.update(state => ({
        ...state,
        selectedSchedule: null
    }));
}
