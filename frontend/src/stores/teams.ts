// a store for fetched teams
import { writable } from 'svelte/store';
import type { Team } from '$lib/types/team';

export const teams = writable([] as Team[]);

export function setTeams(newTeams: Team[]) {
    teams.update(() => [...newTeams]);
}

export function addTeam(team: Team) {
    teams.update(teams => [...teams, team]);
}

export function updateTeam(updatedTeam: Team) {
    teams.update(teams => {
        const index = teams.findIndex(t => t.team_id === updatedTeam.team_id);
        if (index !== -1) {
            teams[index] = updatedTeam;
        }
        return teams;
    });
}

export function deleteTeam(teamId: number) {
    teams.update(teams => teams.filter(t => t.team_id !== teamId));
}