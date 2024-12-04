<script lang="ts">
    import { facilityStatus } from '../../stores/facilityStatus';
    
    export let facilities: Array<{
        facility_id: number;
        name: string;
        is_primary: boolean;
    }>;

    function handleSelect(event: Event) {
        const facility = facilities.find(
            f => f.facility_id === parseInt((event.target as HTMLSelectElement).value)
        );
        if (facility) {
            facilityStatus.update(status => ({
                ...status!,
                selectedFacility: facility
            }));
        }
    }
</script>

<select 
    on:change={handleSelect} 
    value={$facilityStatus.selectedFacility?.facility_id}
>
    {#each facilities as facility}
        <option value={facility.facility_id}>
            {facility.name}
            {#if facility.is_primary}(Primary){/if}
        </option>
    {/each}
</select>