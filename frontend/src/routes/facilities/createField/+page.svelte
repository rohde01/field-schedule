<script lang="ts">
    import CreateField from '$lib/components/createField.svelte';
    import { facilityStatus } from '../../../stores/facilityStatus';
    
    $: facilityId = $facilityStatus.selectedFacility?.facility_id;
</script>

{#if facilityId}
    <CreateField {facilityId} />
{:else}
    <p>Please select a facility first</p>
{/if}