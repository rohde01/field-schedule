import { writable, derived } from 'svelte/store';
import type { FacilityStatus } from '$lib/types/facilityStatus';

// Only load from localStorage if it exists and we're in a browser
const storedStatus = typeof localStorage !== 'undefined' && localStorage.getItem('facilityStatus')
    ? JSON.parse(localStorage.getItem('facilityStatus') || 'null')
    : null;

function createFacilityStore() {
    const { subscribe, set: setStore, update: updateStore } = writable<FacilityStatus>(storedStatus || {
        selectedFacility: null,
        has_facilities: false,
        fields: []
    });

    return {
        subscribe,
        set: (value: FacilityStatus) => {
            const safeValue = {
                ...value,
                fields: value.fields || []
            };
            setStore(safeValue);
            
            // Only persist if there's actual facility data
            if (typeof localStorage !== 'undefined') {
                if (safeValue.selectedFacility) {
                    localStorage.setItem('facilityStatus', JSON.stringify(safeValue));
                } else {
                    localStorage.removeItem('facilityStatus');
                }
            }
        },
        update: (updater: (state: FacilityStatus) => FacilityStatus) => {
            updateStore(state => {
                const updated = updater(state);
                const safeValue = {
                    ...updated,
                    fields: updated.fields || []
                };
                
                // Only persist if there's actual facility data
                if (typeof localStorage !== 'undefined') {
                    if (safeValue.selectedFacility) {
                        localStorage.setItem('facilityStatus', JSON.stringify(safeValue));
                    } else {
                        localStorage.removeItem('facilityStatus');
                    }
                }
                
                return safeValue;
            });
        },
        setFacility: async (facility: FacilityStatus['selectedFacility']) => {
            if (!facility) {
                updateStore(status => ({ ...status, selectedFacility: null, fields: [] }));
                if (typeof localStorage !== 'undefined') {
                    localStorage.removeItem('facilityStatus');
                }
                return;
            }

            updateStore(status => ({ ...status, selectedFacility: facility }));

            try {
                const response = await fetch(`/api/teams/${facility.facility_id}`);
                if (!response.ok) {
                    console.error('Failed to fetch fields:', response.statusText);
                    updateStore(status => ({ ...status, fields: [] }));
                    return;
                }
                const fields = await response.json();
                
                updateStore(status => ({ ...status, fields }));
            } catch (error) {
                console.error('Error fetching fields:', error);
                updateStore(status => ({ ...status, fields: [] }));
            }
        },
        reset: () => {
            if (typeof localStorage !== 'undefined') {
                localStorage.removeItem('facilityStatus');
            }
            setStore({
                selectedFacility: null,
                has_facilities: false,
                fields: []
            });
        },
        removeField: (fieldId: number) => {
            updateStore(status => ({
                ...status,
                fields: status.fields.filter(field => field.field_id !== fieldId)
            }));
        }
    };
}

export const facilityStatus = createFacilityStore();

// Subscribe to store changes to update localStorage and log updates
facilityStatus.subscribe((value) => {
    if (typeof localStorage !== 'undefined') {
        if (value.selectedFacility) {
            localStorage.setItem('facilityStatus', JSON.stringify(value));
        }
        console.log('Facility status updated:', { 
            facility: value.selectedFacility?.name,
            fieldCount: value.fields.length,
            has_facilities: value.has_facilities 
        });
    }
});