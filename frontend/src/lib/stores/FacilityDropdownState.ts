import type { Facility } from '$lib/schemas/facility';
import { writable } from 'svelte/store';
import { facilities } from './facilities';

type FacilityDropdownState = {
    isOpen: boolean;
    selectedFacility: Facility | null;
};

const initialState: FacilityDropdownState = {
    isOpen: false,
    selectedFacility: null
};

export const dropdownState = writable<FacilityDropdownState>(initialState);

facilities.subscribe(facilityList => {
    const primaryFacility = facilityList.find(f => f.is_primary);
    if (primaryFacility) {
        dropdownState.update(state => ({
            ...state,
            selectedFacility: primaryFacility
        }));
    }
});

dropdownState.subscribe(state => {
    if (state.selectedFacility) {
        console.log('Selected facility changed:', state.selectedFacility);
    }
});

export function toggleDropdown(key: keyof Pick<FacilityDropdownState, 'isOpen'>) {
    dropdownState.update(state => ({
        ...state,
        [key]: !state[key]
    }));
}

export function selectFacility(facility: Facility) {
    dropdownState.update(state => ({
        ...state,
        selectedFacility: facility,
    }));
}
