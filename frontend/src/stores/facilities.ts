import { writable } from 'svelte/store';
import type { Facility } from '$lib/schemas/facility';

export const facilities = writable([] as Facility[]);

export function setFacilities(newFacilities: Facility[]) {
    facilities.update(() => [...newFacilities]);
}

export function addFacility(facility: Facility) {
    facilities.update(facilities => [...facilities, facility]);
}