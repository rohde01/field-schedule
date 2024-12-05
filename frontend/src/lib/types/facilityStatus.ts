export interface Facility {
    facility_id: number;
    name: string;
    is_primary: boolean;
}

export interface FieldAvailability {
    day_of_week: string;
    start_time: string;
    end_time: string;
}

export interface SubField {
    field_id: number;
    name: string;
}

export interface Field {
    field_id: number;
    name: string;
    size: string;
    field_type: string;
    parent_field_id: number | null;
    availability: Record<string, FieldAvailability>;
    quarter_subfields: SubField[];
    half_subfields: SubField[];
}

export interface FacilityStatus {
    selectedFacility: Facility | null;
    has_facilities: boolean;
    fields: Field[];
}

declare global {
    namespace App {
        interface Locals {
            facilityStatus: FacilityStatus | null;
        }
    }
}