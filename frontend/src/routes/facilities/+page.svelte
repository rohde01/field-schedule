<script lang="ts">
    import type { PageData, ActionData } from './$types';
    import type { Facility } from '$lib/types/facilityStatus';
    import FacilityDropdown from '$lib/components/FacilityDropdown.svelte';
    import { facilityStatus } from '../../stores/facilityStatus';
    import { browser } from '$app/environment';

    export let data: PageData;
    export let form: ActionData;

    if (browser && data.facilities.length > 0) {
        facilityStatus.update(status => ({
            ...status,
            has_facilities: true
        }));

        // Set primary facility if none selected
        if (!$facilityStatus.selectedFacility) {
            const primaryFacility = data.facilities.find((f: Facility) => f.is_primary);
            if (primaryFacility) {
                facilityStatus.update(status => ({
                    ...status,
                    selectedFacility: primaryFacility
                }));
            }
        }
    }

    $: if (form?.facility) {
        data.facilities = [...data.facilities, form.facility];
        facilityStatus.update(status => ({
            ...status,
            selectedFacility: form.facility,
            has_facilities: true
        }));
    }
</script>

<h1>Facilities</h1>

<FacilityDropdown facilities={data.facilities} />
