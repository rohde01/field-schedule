import { writable } from 'svelte/store';
import type { Team } from '$lib/types/team';

type TeamDropdownState = {
    teamsOpen: boolean;
    selectedTeam: Team | null;
    showCreateTeam: boolean;
};

const initialState: TeamDropdownState = {
    teamsOpen: false,
    selectedTeam: null,
    showCreateTeam: false,
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
