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
    import type { Constraint, ScheduleEntry } from '$lib/schemas/schedule';
    import SuperDebug from 'sveltekit-superforms';
    import { onDestroy } from 'svelte';

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

    // Function to convert schedule entry to a constraint
    function entryToConstraint(entry: ScheduleEntry): Constraint {

        const startTime = parseTimeToMinutes(entry.start_time);
        const endTime = parseTimeToMinutes(entry.end_time);
        
        let durationMinutes = endTime - startTime;
        if (durationMinutes < 0) {
            durationMinutes += 24 * 60;
        }
        const length = Math.max(1, Math.round(durationMinutes / 15));
        
        return {
            team_id: entry.team_id || 0,
            required_field: entry.field_id || null,
            required_cost: null,
            sessions: 1,
            length,
            day_of_week: entry.week_day,
            partial_field: null,
            partial_cost: null,
            partial_time: null,
            start_time: entry.start_time,
            constraint_type: 'specific',
            schedule_entry_id: entry.schedule_entry_id
        };
    }

    function parseTimeToMinutes(timeString: string): number {
        const [hours, minutes] = timeString.split(':').map(Number);
        return hours * 60 + minutes;
    }

    // Subscribe to schedules store and sync entries to form constraints
    const unsubscribe = schedules.subscribe(currentSchedules => {
        const tempSchedules = currentSchedules.filter(s => s.schedule_id < 0);
        
        if (tempSchedules.length === 0) {
            return;
        }
        
        const allEntries = tempSchedules.flatMap(s => s.entries);
        const specificConstraints = allEntries.map(entryToConstraint);
        const teamIds = Array.from(new Set(
            allEntries
                .filter(entry => entry.team_id !== null && entry.team_id !== undefined)
                .map(entry => entry.team_id!)
        ));
        
        // Update form with constraints from entries
        form.update(currentForm => {
            const existingConstraints = currentForm.constraints || [];
            const manualConstraints = existingConstraints.filter(
                (c: Constraint) => c.schedule_entry_id === undefined || c.schedule_entry_id === null
            );
            
            return {
                ...currentForm,
                team_ids: Array.from(new Set([
                    ...(currentForm.team_ids || []),
                    ...teamIds
                ])),
                constraints: [
                    ...manualConstraints,
                    ...specificConstraints
                ]
            };
        });
    });
    onDestroy(unsubscribe);

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
                { label: 'Partial Size', value: field.partial_cost },
                { label: 'Partial Size', value: field.partial_field }
            ].filter(item => item.value != null).map(item => ({ ...item, value: item.value ?? '' }));

            const column2Fields = [
                { label: 'Required Size', value: field.required_cost, style: 'pill' },
                { label: 'Partial Time', value: field.partial_time, style: 'pill' }
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

    <div class="main-content">
        {#if $SidebarDropdownState.showCreateSchedule}
            <div class="create-schedule-section">
                {#if $form.schedule_name}
                    <CreateConstraints {form} {errors} />
                {/if}
                <CreateSchedule {form} {enhance} {errors} />
            </div>
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
            <div class="selected-schedule-section">
                <Dnd />
            </div>
        {/if}

        {#if !$SidebarDropdownState.showCreateSchedule && !$dropdownState.selectedSchedule && !$SidebarDropdownState.selectedConstraint}
            <div class="text-center p-8 text-sage-500">
                Select a schedule or create a new one
            </div>
        {/if}
    </div>
</div>
<div class="mt-8">
    <div class="debug-container">
        <SuperDebug data={$form} collapsible={true} />
    </div>
</div>