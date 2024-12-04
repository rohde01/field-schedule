export interface FacilityStatus {
    selectedFacility: {
        facility_id: number;
        name: string;
        is_primary: boolean;
    } | null;
    has_facilities: boolean;
}

declare global {
    namespace App {
        interface Locals {
            facilityStatus: FacilityStatus | null;
        }
    }
}