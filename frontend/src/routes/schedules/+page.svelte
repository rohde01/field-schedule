<script lang="ts">
    import type { PageData } from './$types';
    import { setSchedules } from '$stores/schedules';
    import Calendar from '$lib/components/Calendar.svelte';
    import SchedulesDropdown from '$lib/components/SchedulesDropdown.svelte';
    import SchedulesSidebar from '$lib/components/SchedulesSidebar.svelte';
    import { SidebarDropdownState } from '$stores/ScheduleSidebarState';
    import CreateConstraints from '$lib/components/CreateConstraints.svelte';
    import { teams, setTeams } from '$stores/teams';
    import SuperDebug from 'sveltekit-superforms';
    import { superForm } from 'sveltekit-superforms/client';

    let { data }: { data: PageData } = $props();
    const { form: rawForm } = data;
    const { form, enhance } = superForm(rawForm);

    $effect(() => {
        if (data.schedules) {
            setSchedules(data.schedules);
        }

        if (data.teams) {
            setTeams(data.teams);
        }
    });

    
</script>

<div class="flex flex-col gap-4">
    <div class="sidebar-container">
        <SchedulesDropdown />
        <SchedulesSidebar teams={$teams} {form} />
    </div>

    {#if $SidebarDropdownState.selectedTeam || $SidebarDropdownState.showCreateSchedule}
        <div class="detail-card-container">
            {#if $SidebarDropdownState.showCreateSchedule}
                <CreateConstraints {form} />
            {:else if $SidebarDropdownState.selectedTeam}
               not implemented
            {/if}
        </div>
    {:else}
        <div class="text-center p-8 text-sage-500">
            Please select a team to view details
        </div>
    {/if}
</div>

<div class="mt-8">
    <div class="debug-container">
        <SuperDebug data={$form} collapsible={true} />
    </div>
</div>
