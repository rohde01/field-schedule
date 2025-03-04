import { writable } from 'svelte/store';
import type { Team } from '$lib/schemas/team';
import type { Constraint } from '$lib/schemas/schedule';
import { dropdownState } from './ScheduleDropdownState';

type SidebarDropdownState = {
    teamsOpen: boolean;
    selectedTeam: Team | null;
    showCreateSchedule: boolean;
    selectedConstraint: Constraint | null;
};

const initialState: SidebarDropdownState = {
    teamsOpen: true,
    selectedTeam: null,
    showCreateSchedule: false,
    selectedConstraint: null
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

export function selectConstraint(constraint: Constraint | null) {
    SidebarDropdownState.update(state => ({
        ...state,
        selectedConstraint: state.selectedConstraint?.constraint_id === constraint?.constraint_id ? null : constraint
    }));
}

export function toggleCreateSchedule() {
    SidebarDropdownState.update(state => {
        const newState = {
            ...state,
            showCreateSchedule: !state.showCreateSchedule,
            selectedConstraint: !state.showCreateSchedule ? null : state.selectedConstraint
        };
        return newState;
    });
    dropdownState.update(state => ({
        ...state,
        selectedSchedule: null
    }));
}
