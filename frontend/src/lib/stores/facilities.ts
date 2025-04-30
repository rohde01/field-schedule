import { writable } from 'svelte/store';
import type { Facility } from '$lib/schemas/facility';
import { facilitySchema } from '$lib/schemas/facility';

export const facilities = writable([] as Facility[]);
export const selectedFacility = writable<Facility | null>(null);
export const showCreateFacility = writable(false);

export function setFacilities(newFacilities: Facility[]) {
    const parsed = newFacilities.map(f => facilitySchema.parse(f));
    facilities.set(parsed);
}

export function addFacility(facility: Facility) {
    const parsed = facilitySchema.parse(facility);
    facilities.update(list => [...list, parsed]);
}

export function setSelectedFacility(facility: Facility | null) {
    selectedFacility.set(facility);
}

export function toggleCreateFacility(show?: boolean) {
    showCreateFacility.update(current => show !== undefined ? show : !current);
}