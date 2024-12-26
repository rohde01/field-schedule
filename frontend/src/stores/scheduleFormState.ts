import { writable } from 'svelte/store';

export const selectedTeamIds = writable<number[]>([]);

selectedTeamIds.subscribe(value => {
    console.log('selectedTeamIds changed:', value);
});

export function toggleTeamSelection(teamId: number) {
    selectedTeamIds.update(ids => {
        if (ids.includes(teamId)) {
            return ids.filter(id => id !== teamId);
        }
        return [...ids, teamId];
    });
}
