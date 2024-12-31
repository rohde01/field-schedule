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
    import CreateSchedule from '$lib/components/CreateSchedule.svelte';

    let { data }: { data: PageData } = $props();
    const { form: rawForm } = data;

    const { form, enhance, errors, message } = superForm(rawForm, {
        dataType: 'json',
        taintedMessage: null,
        id: 'schedule-form',
        onError: (err) => {
            console.error('Form submission error:', err);
        },
        onUpdate: ({ form }) => {
            console.log('Form data being submitted:', form.data);
        },
        onResult: ({ result }) => {
            console.log('Form submission result:', result);
        }
    });

    $effect(() => {
        if (data.schedules) {
            setSchedules(data.schedules);
        }

        if (data.teams) {
            setTeams(data.teams);
        }
    });

    
</script>

<div class="page-container">
    <div class="sidebar">
        <div class="sidebar-content">
            <SchedulesSidebar teams={$teams} {form} />
        </div>
        <div class="sidebar-footer">
            <SchedulesDropdown />
        </div>
    </div>

    {#if $SidebarDropdownState.selectedTeam || $SidebarDropdownState.showCreateSchedule}
        <div class="main-content">
            {#if $SidebarDropdownState.showCreateSchedule}
                <CreateConstraints {form} {errors} />
                <CreateSchedule {form} {enhance} />
            {:else if $SidebarDropdownState.selectedTeam}
               not implemented
            {/if}
        </div>
    {:else}
        <div class="main-content text-center p-8 text-sage-500">
            Please select a team to view details
        </div>
    {/if}
</div>

<!-- <div class="mt-8">
    <div class="debug-container">
        <SuperDebug data={$form} collapsible={true} />
    </div>
</div> -->