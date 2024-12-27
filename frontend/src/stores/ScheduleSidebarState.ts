import { writable } from 'svelte/store';
import type { Team } from '$lib/schemas/team';

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

export const SidebarDropdownState = writable<SidebarDropdownState>(initialState);

export function toggleDropdown(key: keyof Pick<SidebarDropdownState, 'teamsOpen'>) {
    SidebarDropdownState.update(state => ({
        ...state,
        [key]: !state[key]
    }));
}

export function selectTeam(team: Team) {
    SidebarDropdownState.update(state => ({
        ...state,
        selectedTeam: team,
        showCreateTeam: false
    }));
}

export function toggleCreateSchedule() {
    SidebarDropdownState.update(state => ({
        ...state,
        showCreateSchedule: !state.showCreateSchedule,
        selectedSchedule: null
    }));
}
