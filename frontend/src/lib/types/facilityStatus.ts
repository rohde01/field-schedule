export interface Facility {
    facility_id: number;
    name: string;
    is_primary: boolean;
}

export interface FacilityStatus {
    selectedFacility: Facility | null;
    has_facilities: boolean;
}

declare global {
    namespace App {
        interface Locals {
            facilityStatus: FacilityStatus | null;
        }
    }
}