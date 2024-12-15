import { writable } from 'svelte/store';
import type { Field } from '$lib/schemas/field';

export const fields = writable<Field[]>([]);

export function setFields(newFields: Field[]) {
    fields.set(newFields);
}

export function addField(field: Field) {
    fields.update(fields => [...fields, field]);
}

export function deleteField(fieldId: number) {
    fields.update(fields => fields.filter(f => f.field_id !== fieldId));
}

export function getFieldById(fieldId: number): Field | undefined {
    let result: Field | undefined;
    fields.subscribe(fields => {
        result = fields.find(f => f.field_id === fieldId);
    })();
    return result;
}

export function getFieldsByFacility(facilityId: number): Field[] {
    let result: Field[] = [];
    fields.subscribe(fields => {
        result = fields.filter(f => f.facility_id === facilityId);
    })();
    return result;
}