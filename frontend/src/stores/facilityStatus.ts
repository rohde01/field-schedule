import { writable } from 'svelte/store';
import type { FacilityStatus } from '$lib/types/facilityStatus';

const storedStatus = typeof localStorage !== 'undefined' 
    ? JSON.parse(localStorage.getItem('facilityStatus') || 'null')
    : null;

export const facilityStatus = writable<FacilityStatus>(storedStatus || {
    selectedFacility: null,
    has_facilities: false
});

facilityStatus.subscribe((value) => {
    if (typeof localStorage !== 'undefined') {
        localStorage.setItem('facilityStatus', JSON.stringify(value));
    }
    console.log('facility store updated:', value);
});