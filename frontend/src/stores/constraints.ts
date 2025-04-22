// a store for fetched constraints
import { writable } from 'svelte/store';
import type { Constraint } from '$lib/schemas/constraint';

export const constraints = writable([] as Constraint[]);

constraints.subscribe(value => {
    console.log('Constraints store updated:', value);
});

export function setConstraints(newConstraints: Constraint[]) {
    constraints.update(() => [...newConstraints]);
}

export function addConstraint(constraint: Constraint) {
    constraints.update(constraints => [...constraints, constraint]);
}

export function deleteConstraint(constraint_id: number) {
    constraints.update(constraints => constraints.filter(t => t.team_id !== constraint_id));
}