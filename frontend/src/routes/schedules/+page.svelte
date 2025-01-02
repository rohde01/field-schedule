<script lang="ts">
    import type { PageData } from './$types';
    import { schedules } from '$stores/schedules';
    import SchedulesDropdown from '$lib/components/SchedulesDropdown.svelte';
    import SchedulesSidebar from '$lib/components/SchedulesSidebar.svelte';
    import { SidebarDropdownState } from '$stores/ScheduleSidebarState';
    import { dropdownState, selectSchedule } from '$stores/ScheduleDropdownState';
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
        onError: ({ result }) => {
            if ('error' in result) {
                errorMessage = typeof result.error === 'string' 
                    ? result.error 
                    : result.error instanceof Error 
                        ? result.error.message 
                        : 'message' in result.error
                            ? result.error.message
                            : 'An unexpected error occurred';
                showErrorModal = true;
            }
        },
        onUpdate: ({ form }) => {
        },
        onResult: ({ result }) => {
            if (result.type === 'failure') {
                const failureResult = result as { data: { errors?: { _errors?: string[] } } };
                if (failureResult.data?.errors?._errors?.length) {
                    errorMessage = failureResult.data.errors._errors[0];
                    showErrorModal = true;
                }
            }
            else if (result.type === 'success' && result.data && 'schedule_id' in result.data) {
                pendingScheduleId = result.data.schedule_id;
            }
        }
    });

    let showErrorModal = $state(false);
    let errorMessage = $state('');

    $effect(() => {
        const errorMessages = $errors?._errors;
        if (Array.isArray(errorMessages) && errorMessages.length > 0) {
            errorMessage = errorMessages[0];
            showErrorModal = true;
        }
    });

    function closeErrorModal() {
        showErrorModal = false;
    }
</script>

{#if showErrorModal}
    <div class="modal-overlay">
        <div class="modal-container">
            <h3 class="modal-title">Schedule Creation Error</h3>
            <p class="modal-description">{errorMessage}</p>
            <div class="modal-actions">
                <button 
                    class="btn btn-secondary"
                    onclick={closeErrorModal}
                >
                    Close
                </button>
            </div>
        </div>
    </div>
{/if}

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