import { writable } from 'svelte/store';
import type { Facility } from '$lib/schemas/facility';

export const facilities = writable([] as Facility[]);
export const selectedFacility = writable<Facility | null>(null);
export const showCreateFacility = writable(false);

export function setFacilities(newFacilities: Facility[]) {
    facilities.update(() => [...newFacilities]);
}

export function addFacility(facility: Facility) {
    facilities.update(facilities => [...facilities, facility]);
}

export function setSelectedFacility(facility: Facility | null) {
    selectedFacility.set(facility);
}

export function toggleCreateFacility(show?: boolean) {
    showCreateFacility.update(current => show !== undefined ? show : !current);
}