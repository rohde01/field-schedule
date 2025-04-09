import { fieldSchema, type Field, type FieldAvailability } from '$lib/schemas/field';

export function processFields(rawFields: any[], availabilities: any[]): Field[] {
    const fields: Field[] = [];
    
    for (const field of rawFields || []) {
        if (field.field_type === 'full') {
            // Find all direct half-fields for this full field
            const halfSubfields = (rawFields || []).filter(f => 
                f.parent_field_id === field.field_id && f.field_type === 'half'
            );
            
            // Find all quarter-fields (these are children of half-fields)
            const quarterSubfields = (rawFields || []).filter(f => {
                // Get IDs of all the half-fields
                const halfFieldIds = halfSubfields.map(hf => hf.field_id);
                // Return true if this field is a quarter field and its parent is one of our half-fields
                return f.field_type === 'quarter' && halfFieldIds.includes(f.parent_field_id);
            });

            // Group availabilities by day of week for this field
            const fieldAvailability: Record<string, FieldAvailability> = {};
            (availabilities || [])
                .filter(a => a.field_id === field.field_id)
                .forEach(a => {
                    fieldAvailability[a.day_of_week] = {
                        day_of_week: a.day_of_week,
                        start_time: a.start_time.substring(0, 5), // Format as HH:MM
                        end_time: a.end_time.substring(0, 5),     // Format as HH:MM
                        club_id: a.club_id
                    };
                });

            try {
                // Validate and push the processed field
                const validatedField = fieldSchema.parse({
                    field_id: field.field_id,
                    facility_id: field.facility_id,
                    club_id: field.club_id,
                    name: field.name,
                    size: field.size,
                    field_type: field.field_type,
                    parent_field_id: field.parent_field_id,
                    is_active: field.is_active,
                    availability: fieldAvailability,
                    half_subfields: halfSubfields,
                    quarter_subfields: quarterSubfields
                });
                
                fields.push(validatedField);
            } catch (validationError) {
                console.error('Field validation failed:', validationError, field);
                // Skip invalid fields rather than failing the whole request
            }
        }
    }
    
    return fields;
}