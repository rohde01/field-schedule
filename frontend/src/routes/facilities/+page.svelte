<script lang="ts">
    import type { PageData, ActionData } from './$types';
    import type { Facility, FacilityStatus } from '$lib/types/facilityStatus';
    import FacilityDropdown from '$lib/components/FacilityDropdown.svelte';
    import FieldsDropdown from '$lib/components/FieldsDropdown.svelte';
    import { facilityStatus } from '../../stores/facilityStatus';
    import { browser } from '$app/environment';
    import { invalidate } from '$app/navigation';
    import { onMount } from 'svelte';
    import { dropdownState, setDefaultField, initializeDropdownState, resetFieldsState } from '../../stores/dropdownState';
    import { page } from '$app/stores';

    export let data: PageData;
    export let form: ActionData;

    let isInitializing = true;

    $: if ($page.url.pathname === '/facilities') {
        initializeDropdownState();
    }

    // On initial load, update the store with the fields from the server
    onMount(async () => {
        if (browser) {
            initializeDropdownState();
            
            facilityStatus.update((status: FacilityStatus) => ({
                ...status,
                has_facilities: data.has_facilities,
                fields: data.fields || []
            }));

            if (data.fields && data.fields.length > 0) {
                setDefaultField(data.fields);
            }

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

    // Watch for facility changes
    $: if ($facilityStatus.selectedFacility) {
        resetFieldsState();
        invalidate('app:facilities');
    }

    // Watch for fields updates
    $: if ($facilityStatus.fields && $facilityStatus.fields.length > 0) {
        setDefaultField($facilityStatus.fields);
    }

    $: if ($facilityStatus.selectedFacility) {
        invalidate('app:facilities');
    }
</script>

<div class="flex flex-col gap-4">
    <div class="flex justify-between items-center">
        <div class="w-72">
            <FacilityDropdown facilities={data.facilities} />
        </div>
    </div>

    {#if !isInitializing}
        {#if $facilityStatus.selectedFacility}
            {#if $facilityStatus.fields && $facilityStatus.fields.length > 0}
                <FieldsDropdown fields={$facilityStatus.fields} />
            {:else}
                <div class="text-center p-8 text-sage-500">
                    No fields available for this facility
                </div>
            {/if}
        {:else}
            <div class="text-center p-8 text-sage-500">
                Please select a facility to view fields
            </div>
        {/if}
    {:else}
        <div class="spinner-container">
            <div class="spinner"></div>
        </div>
    {/if}
</div>
