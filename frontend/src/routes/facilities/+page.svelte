<script lang="ts">
    import type { PageData, ActionData } from './$types';
    import type { Facility, FacilityStatus } from '$lib/types/facilityStatus';
    import FacilityDropdown from '$lib/components/FacilityDropdown.svelte';
    import { facilityStatus } from '../../stores/facilityStatus';
    import { browser } from '$app/environment';
    import { invalidate } from '$app/navigation';
    import { onMount } from 'svelte';

    export let data: PageData;
    export let form: ActionData;

    let isInitializing = true;

    // On initial load, update the store with the fields from the server
    onMount(async () => {
        if (browser) {
            facilityStatus.update((status: FacilityStatus) => ({
                ...status,
                has_facilities: data.has_facilities,
                fields: data.fields || []
            }));

            if ($facilityStatus.selectedFacility && (!$facilityStatus.fields || $facilityStatus.fields.length === 0)) {
                await facilityStatus.setFacility($facilityStatus.selectedFacility);
            }
            else if (data.has_facilities && data.facilities.length > 0 && !$facilityStatus.selectedFacility) {
                const primaryFacility = data.facilities.find((f: Facility) => f.is_primary);
                if (primaryFacility) {
                    await facilityStatus.setFacility(primaryFacility);
                }
            }
            isInitializing = false;
        }
    });

    $: if (form?.facility) {
        data.facilities = [...data.facilities, form.facility];
        facilityStatus.setFacility(form.facility);
    }

    $: if ($facilityStatus.selectedFacility) {
        invalidate('app:facilities');
    }
</script>

<div class="flex flex-col gap-4 p-4">
    <div class="flex justify-between items-center">
        <h1 class="text-2xl font-bold">Facilities</h1>
        <FacilityDropdown facilities={data.facilities} />
    </div>

    {#if isInitializing}
        <div class="spinner-container">
            <div class="spinner"></div>
        </div>
    {:else if !$facilityStatus.has_facilities}
        <div class="text-center bg-white p-8 rounded-lg shadow-md">
            <h2 class="text-2xl font-bold mb-4">Welcome to Field Schedule!</h2>
            <p class="text-gray-600 mb-6">
                It looks like you haven't set up any facilities yet. To get started, click the "+" button 
                in the facility dropdown above to create your first facility.
            </p>
        </div>
    {:else}
        {#if $facilityStatus.selectedFacility}
            <div class="flex flex-col gap-4">
                <h2 class="text-xl font-semibold">Fields for {$facilityStatus.selectedFacility.name}</h2>
                {#if $facilityStatus.fields.length > 0}
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {#each $facilityStatus.fields as field}
                            <div class="bg-white p-4 rounded-lg shadow">
                                <h3 class="font-medium">{field.name}</h3>
                                <p class="text-sm text-gray-600">Size: {field.size}</p>
                                <p class="text-sm text-gray-600">Type: {field.field_type}</p>
                            </div>
                        {/each}
                    </div>
                {:else}
                    <p class="text-gray-600">No fields available for this facility.</p>
                {/if}
            </div>
        {:else}
            <p class="text-gray-600">Select a facility to view its fields.</p>
        {/if}
    {/if}
</div>
