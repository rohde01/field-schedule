import { writable } from 'svelte/store';

interface DropdownState {
    facilityOpen: boolean;
    fieldsOpen: boolean;
}

const dropdownState = writable<DropdownState>({
    facilityOpen: false,
    fieldsOpen: true  // Set default to true so fields are visible by default
});

let previousFieldsState = true;  

export { dropdownState };

export function closeAllDropdowns() {
    dropdownState.update(state => ({
        ...state,
        facilityOpen: false,
        fieldsOpen: false
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
