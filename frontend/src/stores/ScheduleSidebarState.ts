import { writable } from 'svelte/store';
import type { Team } from '$lib/schemas/team';
import type { Constraint } from '$lib/schemas/constraint';
import { dropdownState } from './ScheduleDropdownState';

interface SidebarState {
    teamsOpen: boolean;
    selectedTeam: Team | null;
    showCreateSchedule: boolean;
    selectedConstraint: Constraint | null;
}

export const SidebarDropdownState = writable<SidebarState>({
    teamsOpen: true,
    selectedTeam: null,
    showCreateSchedule: false,
    selectedConstraint: null
});

export const toggleDropdown = (key: 'teamsOpen') => {
    SidebarDropdownState.update(state => ({
        ...state,
        [key]: !state[key]
    }));
};

export const toggleCreateSchedule = () => {
    SidebarDropdownState.update(state => ({
        ...state,
        showCreateSchedule: !state.showCreateSchedule,
        selectedTeam: null,
        selectedConstraint: null
    }));
    dropdownState.update(state => ({
        ...state,
        selectedSchedule: null
    }));
};

export const selectTeam = (team: Team) => {
    SidebarDropdownState.update(state => ({
        ...state,
        selectedTeam: state.selectedTeam?.team_id === team.team_id ? null : team,
        selectedConstraint: null
    }));
};

export const selectConstraint = (constraint: Constraint | null) => {
    SidebarDropdownState.update(state => ({
        ...state,
        selectedConstraint: constraint
    }));
};
