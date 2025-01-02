<script lang="ts">
    import type { PageData } from './$types';
    import Dnd from '$lib/components/dnd.svelte';
    import SchedulesDropdown from '$lib/components/SchedulesDropdown.svelte';
    export let data: PageData;
</script>

<h1>Welcome, {data.firstName}!</h1>

<div class="flex flex-col min-h-screen">
    <div class="flex-grow">
        <Dnd />
    </div>
    <div class="mt-auto p-4">
        <SchedulesDropdown />
    </div>
</div>