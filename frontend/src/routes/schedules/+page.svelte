<script lang="ts">
    import type { PageData } from './$types';
    import { setSchedules, schedules } from '$stores/schedules';
    import SchedulesDropdown from '$lib/components/SchedulesDropdown.svelte';
    import SchedulesSidebar from '$lib/components/SchedulesSidebar.svelte';
    import { SidebarDropdownState } from '$stores/ScheduleSidebarState';
    import { dropdownState, selectSchedule } from '$stores/ScheduleDropdownState';
    import CreateConstraints from '$lib/components/CreateConstraints.svelte';
    import { teams, setTeams } from '$stores/teams';
    import { superForm } from 'sveltekit-superforms/client';
    import CreateSchedule from '$lib/components/CreateSchedule.svelte';
    import Dnd from '$lib/components/dnd.svelte'
    import DisplayCard, { type Column } from '$lib/components/DisplayCard.svelte';
    import { constraints } from '$stores/constraints';
    import type { Constraint } from '$lib/schemas/schedule';


    let { data }: { data: PageData } = $props();
    const { form: rawForm } = data;
    let displayColumns: Column[] = $state([]);
    let constraintTitle: string = $state('');

    const deleteForm = superForm(data.deleteForm, {
        onResult: ({ result }) => {
            if (result.type === 'success' && result.data?.schedule_id) {
                handleScheduleDelete(result.data.schedule_id);
            }
        }
    });

    const handleScheduleDelete = (scheduleId: number) => {
        schedules.update(t => t.filter(item => item.schedule_id !== scheduleId));
        dropdownState.update(state => ({ ...state, selectedschedule: null }));
    };

    let pendingScheduleId: number | null = null;

    $effect(() => {
        if (data.schedules) {
            setSchedules(data.schedules);
        }

        if (data.teams) {
            setTeams(data.teams);
        }
    });

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

    const handleFieldDelete = async (constraintId: number) => {
        // Future implementation for deleting a constraint
        console.log('Deleting constraint:', constraintId);
    };

    $effect(() => {
        if ($SidebarDropdownState.selectedConstraint) {
            const field = $constraints.find((f: Constraint) => 
                f.constraint_id === $SidebarDropdownState.selectedConstraint?.constraint_id
            ) || $SidebarDropdownState.selectedConstraint;

            const teamName = $teams.find(t => t.team_id === field.team_id)?.name || 'Unknown Team';
            constraintTitle = `Constraint ID: ${field.constraint_id} | ${teamName}`;

            const column1Fields = [
                { label: 'Sessions', value: field.sessions },
                { label: 'Length', value: field.length },
                { label: 'Start Time', value: field.start_time },
                { label: 'Partial Size', value: field.partial_ses_space_cost },
                { label: 'Partial Size', value: field.partial_ses_space_size }
            ].filter(item => item.value != null).map(item => ({ ...item, value: item.value ?? '' }));

            const column2Fields = [
                { label: 'Required Size', value: field.required_size, style: 'pill' },
                { label: 'Required Size', value: field.required_cost, style: 'pill' },
                { label: 'Subfield Type', value: field.subfield_type, style: 'pill' },
                { label: 'Partial Time', value: field.partial_ses_time, style: 'pill' }
            ].filter(item => item.value != null).map(item => ({ ...item, value: item.value ?? '' }));

            displayColumns = [
                { fields: column1Fields },
                { fields: column2Fields }
            ].filter(column => column.fields.length > 0);
        }
    });
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
            <SchedulesDropdown deleteForm={deleteForm} />
        </div>
    </div>

    {#if $SidebarDropdownState.selectedTeam || $SidebarDropdownState.showCreateSchedule || $dropdownState.selectedSchedule || $SidebarDropdownState.selectedConstraint}
        <div class="main-content">
            {#if $SidebarDropdownState.showCreateSchedule}
                {#if $form.schedule_name}
                    <CreateConstraints {form} {errors} />
                {/if}
                <CreateSchedule {form} {enhance} {errors} />
            {/if}
            
            {#if $SidebarDropdownState.selectedConstraint}
                <DisplayCard 
                    title={constraintTitle}
                    columns={displayColumns}
                    deleteConfig={{
                        enabled: true,
                        itemId: $SidebarDropdownState.selectedConstraint.constraint_id,
                        itemName: constraintTitle,
                        onDelete: handleFieldDelete
                    }}
                />
            {/if}

            {#if $dropdownState.selectedSchedule}
                <Dnd />
            {/if}
        </div>
    {:else}
        <div class="main-content text-center p-8 text-sage-500">
            Please select a team to view details
        </div>
    {/if}
</div>