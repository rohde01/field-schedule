<script lang="ts">
    import Schedule from './Schedule.svelte'
    import { Datepicker, P } from 'flowbite-svelte';
    let dateRange = { from: null, to: null };
    import { Card } from 'flowbite-svelte';

</script>

<main class="relative w-full bg-white dark:bg-gray-800 p-6">
    <div class="mb-4">
        <div class="flex flex-col lg:flex-row gap-6 justify-end">
            <div class="w-72">
                <Datepicker range bind:rangeFrom={dateRange.from} bind:rangeTo={dateRange.to} />
            </div>
        </div>
    </div>
    <div class="mt-6 w-full">
        <Schedule />
    </div>
</main>
<!-- <div class="mt-8">
    <div class="debug-container">
        <SuperDebug data={$form} collapsible={true} />
    </div>
</div> -->