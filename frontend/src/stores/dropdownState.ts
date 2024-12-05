import { writable } from 'svelte/store';
import type { Field } from '$lib/types/facilityStatus';
import { browser } from '$app/environment';

interface DropdownState {
    facilityOpen: boolean;
    fieldsOpen: boolean;
    selectedField: Field | null;
    showCreateField: boolean;
}

// Initialize with defaults
const dropdownState = writable<DropdownState>({
    facilityOpen: false,
    fieldsOpen: true,
    selectedField: null,
    showCreateField: false
});

export function initializeDropdownState() {
    if (browser) {
        dropdownState.update(state => ({
            ...state,
            fieldsOpen: true, // Always ensure fields are open
            showCreateField: false
        }));
    }
}

let previousFieldsState = true;

export { dropdownState };

export function selectField(field: Field | null) {
    dropdownState.update(state => ({
        ...state,
        selectedField: state.selectedField?.field_id === field?.field_id ? null : field,
        showCreateField: false
    }));
}

export function setDefaultField(fields: Field[]) {
    dropdownState.update(state => {
        if (!state.selectedField && fields.length > 0) {
            const default11v11Field = fields.find(field => field.size === '11v11');
            return {
                ...state,
                selectedField: default11v11Field || fields[0],
                fieldsOpen: true 
            };
        }
        return {
            ...state,
            fieldsOpen: true
        };
    });
}

export function resetFieldsState() {
    dropdownState.update(state => ({
        ...state,
        fieldsOpen: true,
        selectedField: null,
        showCreateField: false
    }));
}

export function toggleCreateField() {
    dropdownState.update(state => ({
        ...state,
        showCreateField: !state.showCreateField,
        selectedField: null,
        fieldsOpen: false
    }));
}

export function closeAllDropdowns() {
    dropdownState.update(state => ({
        ...state,
        facilityOpen: false,
        fieldsOpen: false,
        selectedField: null,
        showCreateField: false
    }));
}

export function toggleDropdown(dropdown: keyof DropdownState) {
    dropdownState.update(state => {
        const newState = { ...state };
        
        if (dropdown === 'facilityOpen') {
            if (state.facilityOpen) {
                // When closing facility dropdown, restore previous fields state
                newState.facilityOpen = false;
                newState.fieldsOpen = previousFieldsState;
            } else {
                // When opening facility dropdown, save fields state and close it
                previousFieldsState = state.fieldsOpen;
                newState.facilityOpen = true;
                newState.fieldsOpen = false;
            }
        } else if (dropdown === 'fieldsOpen') {
            newState.fieldsOpen = !state.fieldsOpen;
            previousFieldsState = newState.fieldsOpen;
            if (newState.fieldsOpen) {
                newState.facilityOpen = false;
            }
        }
        
        return newState;
    });
}
