import { writable } from 'svelte/store';
import type { Field, FlattenedField } from '$lib/schemas/field';

export const fields = writable<Field[]>([]);

export function setFields(newFields: Field[]) {
    fields.set(newFields);
}

export function addField(field: Field) {
    fields.update(fields => [...fields, field]);
}

export function updateField(updatedField: Field) {
    fields.update(fields => 
        fields.map(field => field.field_id === updatedField.field_id ? updatedField : field)
    );
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

export function getFlattenedFields(): FlattenedField[] {
    let result: FlattenedField[] = [];
    fields.subscribe(allFields => {

        result = [...allFields] as FlattenedField[];
        
        allFields.forEach(field => {
            if (field.half_subfields && field.half_subfields.length > 0) {
                result = [...result, ...field.half_subfields] as FlattenedField[];
            }
        });
        
        allFields.forEach(field => {
            if (field.quarter_subfields && field.quarter_subfields.length > 0) {
                result = [...result, ...field.quarter_subfields] as FlattenedField[];
            }
        });
    })();
    return result;
}