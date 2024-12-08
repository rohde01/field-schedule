export type FieldSize = '11v11' | '8v8' | '5v5' | '3v3';
export type FieldType = 'full' | 'half' | 'quarter';

export interface SubField {
    name: string;
    field_type: 'half' | 'quarter';
    quarter_fields?: SubField[];
}

export interface Field {
    facility_id: number;
    name: string;
    size: FieldSize;
    field_type: 'full';
    half_fields?: SubField[];
}

export interface CreateFieldResponse {
    field_id: number;
    error?: string;
}

export interface FieldAvailability {
    day_of_week: 'Mon' | 'Tue' | 'Wed' | 'Thu' | 'Fri' | 'Sat' | 'Sun';
    start_time: string;  // HH:MM format
    end_time: string;    // HH:MM format
}

export interface FieldAvailabilityData {
    availabilities: FieldAvailability[];
}
