<script lang="ts">
    import type { PageData } from './$types';
    import FacilityDropdown from '$lib/components/FacilityDropdown.svelte';
    import { facilityStatus } from '../../stores/facilityStatus';
    import { browser } from '$app/environment';

    export let data: PageData;

    if (browser && data.facilities.length > 0) {
        facilityStatus.update(status => ({
            ...status,
            has_facilities: true
        }));

        // Set primary facility if none selected
        if (!$facilityStatus.selectedFacility) {
            const primaryFacility = data.facilities.find(f => f.is_primary);
            if (primaryFacility) {
                facilityStatus.update(status => ({
                    ...status,
                    selectedFacility: primaryFacility
                }));
            }
        }
    }
</script>

<h1>Facilities</h1>
<FacilityDropdown facilities={data.facilities} />
