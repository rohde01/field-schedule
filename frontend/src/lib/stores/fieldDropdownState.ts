import { writable } from 'svelte/store';
import type { Field } from '$lib/schemas/field';

type FieldDropdownState = {
    fieldsOpen: boolean;
    selectedField: Field | null;
    showCreateField: boolean;
};

const initialState: FieldDropdownState = {
    fieldsOpen: true,
    selectedField: null,
    showCreateField: false,
};

export const dropdownState = writable<FieldDropdownState>(initialState);

export function toggleDropdown(key: keyof Pick<FieldDropdownState, 'fieldsOpen'>) {
    dropdownState.update(state => ({
        ...state,
        [key]: !state[key]
    }));
}

export function selectField(field: Field) {
    dropdownState.update(state => ({
        ...state,
        selectedField: field,
        showCreateField: false
    }));
}

export function setDefaultField(fields: Field[]) {
    dropdownState.update(state => {
        if (!state.selectedField && fields.length > 0) {
            return {
                ...state,
                selectedField: fields[0]
            };
        }
        return state;
    });
}

export function toggleCreateField() {
    dropdownState.update(state => ({
        ...state,
        showCreateField: !state.showCreateField,
        selectedField: null
    }));
}
