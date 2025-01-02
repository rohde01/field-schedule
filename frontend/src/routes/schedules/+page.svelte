<script lang="ts">
    import type { PageData } from './$types';
    import { setSchedules, schedules } from '$stores/schedules';
    import SchedulesDropdown from '$lib/components/SchedulesDropdown.svelte';
    import SchedulesSidebar from '$lib/components/SchedulesSidebar.svelte';
    import { SidebarDropdownState } from '$stores/ScheduleSidebarState';
    import { dropdownState, selectSchedule, selectAndShowSchedule } from '$stores/ScheduleDropdownState';
    import CreateConstraints from '$lib/components/CreateConstraints.svelte';
    import { teams, setTeams } from '$stores/teams';
    import SuperDebug from 'sveltekit-superforms';
    import { superForm } from 'sveltekit-superforms/client';
    import CreateSchedule from '$lib/components/CreateSchedule.svelte';
    import Dnd from '$lib/components/dnd.svelte'

    let { data }: { data: PageData } = $props();
    const { form: rawForm } = data;

    let pendingScheduleId: number | null = null;

    $effect(() => {
        const currentSchedules = $schedules; 
        const currentPendingId = pendingScheduleId; 
        
        if (currentPendingId && currentSchedules) {
            const newSchedule = currentSchedules.find(s => s.schedule_id === currentPendingId);
            
            if (newSchedule) {
                selectSchedule(newSchedule);
                pendingScheduleId = null;
            }
        }
    });

    const { form, enhance, errors, message } = superForm(rawForm, {
        dataType: 'json',
        taintedMessage: null,
        id: 'schedule-form',
        onError: (err) => {
            console.error('Form submission error:', err);
        },
        onUpdate: ({ form }) => {
        },
        onResult: ({ result }) => {
            if (result.type === 'success' && result.data && 'schedule_id' in result.data) {
                pendingScheduleId = result.data.schedule_id;
            }
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

    {#if $SidebarDropdownState.selectedTeam || $SidebarDropdownState.showCreateSchedule || $dropdownState.selectedSchedule}
        <div class="main-content">
            {#if $SidebarDropdownState.showCreateSchedule}
                <CreateConstraints {form} {errors} />
                <CreateSchedule {form} {enhance} {errors} />
            {:else if $dropdownState.selectedSchedule}
                <Dnd />
            {:else}
                not implemented
            {/if}
        </div>
    {:else}
        <div class="main-content text-center p-8 text-sage-500">
            Please select a team to view details
        </div>
    {/if}
</div>

<div class="mt-8">
    <div class="debug-container">
        <SuperDebug data={$form} collapsible={true} />
    </div>
</div>