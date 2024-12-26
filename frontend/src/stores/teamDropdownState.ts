import { writable } from 'svelte/store';
import type { Team } from '$lib/schemas/team';

type TeamDropdownState = {
    teamsOpen: boolean;
    selectedTeam: Team | null;
    showCreateTeam: boolean;
    showCreateSchedule: boolean;
};

const initialState: TeamDropdownState = {
    teamsOpen: true,
    selectedTeam: null,
    showCreateTeam: false,
    showCreateSchedule: false
};

export const dropdownState = writable<TeamDropdownState>(initialState);

export function toggleDropdown(key: keyof Pick<TeamDropdownState, 'teamsOpen'>) {
    dropdownState.update(state => ({
        ...state,
        [key]: !state[key]
    }));
}

export function selectTeam(team: Team) {
    dropdownState.update(state => ({
        ...state,
        selectedTeam: team,
        showCreateTeam: false
    }));
}

export function setDefaultTeam(teams: Team[]) {
    dropdownState.update(state => {
        if (!state.selectedTeam && teams.length > 0) {
            return {
                ...state,
                selectedTeam: teams[0]
            };
        }
        return state;
    });
}

export function toggleCreateTeam() {
    dropdownState.update(state => ({
        ...state,
        showCreateTeam: !state.showCreateTeam,
        selectedTeam: null
    }));
}

export function toggleCreateSchedule() {
    dropdownState.update(state => ({
        ...state,
        showCreateSchedule: !state.showCreateSchedule,
        selectedSchedule: null
    }));
}
