<script lang="ts">
    import Schedule from './Schedule.svelte'
    import CreateCard from './CreateCard.svelte'
    import TeamCard from './TeamCard.svelte'
    import { Datepicker, P, Card } from 'flowbite-svelte';
    import { IsCreating } from '$lib/stores/schedules';
    let dateRange = { from: null, to: null };
</script>


    <div id="main-content" class="relative mx-auto h-full w-full overflow-y-auto bg-gray-50 p-4 dark:bg-gray-900">
        {#if $IsCreating}
            <div class="grid grid-cols-1 pt-2 xl:grid-cols-3 xl:gap-4 xl:px-0 dark:bg-gray-900">
                <div class="col-span-full xl:col-auto">
                    <CreateCard />
                </div>
                <div class="col-span-2 xl:col-span-2">
                    <TeamCard />
                </div>
            </div>
        {/if}
        <Schedule />
    </div>

<!-- <div class="mt-8">
    <div class="debug-container">
        <SuperDebug data={$form} collapsible={true} />
    </div>

                <div class="w-72">
                <Datepicker range bind:rangeFrom={dateRange.from} bind:rangeTo={dateRange.to} />
            </div>
</div> -->