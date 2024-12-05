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

    // On initial load, update the store with the fields from the server
    onMount(() => {
        if (browser && data.facilities.length > 0) {
            facilityStatus.update((status: FacilityStatus) => ({
                ...status,
                has_facilities: true
            }));

            if (data.fields?.length > 0) {
                facilityStatus.update((status: FacilityStatus) => ({
                    ...status,
                    fields: data.fields
                }));
            }
            else if (!$facilityStatus.selectedFacility) {
                const primaryFacility = data.facilities.find((f: Facility) => f.is_primary);
                if (primaryFacility) {
                    facilityStatus.setFacility(primaryFacility);
                }
            }
            else if ($facilityStatus.selectedFacility && !$facilityStatus.fields.length) {
                facilityStatus.setFacility($facilityStatus.selectedFacility);
            }
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
</div>
