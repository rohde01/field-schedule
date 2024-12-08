<script lang="ts">
    import type { Field as ViewField } from '$lib/types/facilityStatus';
    import FieldCreateForm from './CreateField.svelte';
    import FieldViewDetails from './DisplayField.svelte';

    export let field: ViewField | null = null;
    export let facilityId: number | undefined = undefined;
    export let isCreateMode = false;
</script>

<div class="field-card" role="presentation" on:mousedown|stopPropagation>
    {#if isCreateMode}
        <FieldCreateForm {facilityId} />
    {:else if field}
        <FieldViewDetails {field} />
    {/if}
</div>
