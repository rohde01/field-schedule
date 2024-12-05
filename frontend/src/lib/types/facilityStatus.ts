export interface Facility {
    facility_id: number;
    name: string;
    is_primary: boolean;
}

export interface Field {
    field_id: number;
    name: string;
    size: string;
    field_type: string;
    parent_field_id: number | null;
    availability: Record<string, any>;
    quarter_subfields: any[];
    half_subfields: any[];
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