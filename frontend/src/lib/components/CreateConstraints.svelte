<script lang="ts">
    import type { ValidationErrors } from 'sveltekit-superforms';
    import EditableField from './EditableField.svelte';
    import type { Constraint } from '$lib/schemas/constraint';
    import type { GenerateScheduleRequest } from '$lib/schemas/schedule';
    import { SidebarDropdownState } from '../stores/ScheduleSidebarState';
    import type { Writable } from 'svelte/store';
    import { writable } from 'svelte/store';
    import { fields } from '../stores/fields';
    
    let autoModeAppliedTeams = writable<Set<number>>(new Set());
    let autoConstraintSessions = writable<Record<number, number>>({});
    
    let { form, errors } = $props<{ 
        form: Writable<GenerateScheduleRequest>,
        errors: Writable<ValidationErrors<GenerateScheduleRequest>>
    }>();

    const selectedTeam = $derived($SidebarDropdownState.selectedTeam);
    const expandedConstraints = writable<Set<number>>(new Set());

    function addConstraint(type: 'specific' | 'flexible') {
        const newConstraint: Constraint = {
            team_id: selectedTeam?.team_id || 0,
            required_field: null,
            required_cost: null,
            sessions: 1,
            length: 1,
            day_of_week: null,
            partial_field: null,
            partial_cost: null,
            partial_time: null,
            start_time: null,
            constraint_type: type
        };

        form.update((f: GenerateScheduleRequest) => ({
            ...f,
            constraints: [...(f.constraints || []), newConstraint]
        }));

        if (selectedTeam?.team_id) {
            form.update((f: GenerateScheduleRequest) => ({
                ...f,
                team_ids: Array.from(new Set([...(f.team_ids || []), selectedTeam.team_id]))
            }));
        }
    }

    function getActualIndex(visibleIndex: number): number {
        if (!$form.constraints) return -1;
        let count = -1;
        return $form.constraints.findIndex((c: Constraint) => {
            if (c.team_id === selectedTeam?.team_id && c.constraint_type !== 'auto') {
                count++;
                return count === visibleIndex;
            }
            return false;
        });
    }

    function removeConstraint(visibleIndex: number) {
        const actualIndex = getActualIndex(visibleIndex);
        if (actualIndex === -1) return;

        form.update((f: GenerateScheduleRequest) => {
            const constraints = [...(f.constraints || [])];
            const removedConstraint = constraints[actualIndex];
            constraints.splice(actualIndex, 1);

            const hasRemainingConstraints = constraints.some(
                c => c.team_id === removedConstraint.team_id
            );
            if (!hasRemainingConstraints) {
                return {
                    ...f,
                    constraints,
                    team_ids: (f.team_ids || []).filter(id => id !== removedConstraint.team_id)
                };
            }

            return {
                ...f,
                constraints
            };
        });
    }

    function togglePartialFields(visibleIndex: number) {
        expandedConstraints.update(expanded => {
            const newExpanded = new Set(expanded);
            if (newExpanded.has(visibleIndex)) {
                newExpanded.delete(visibleIndex);
            } else {
                newExpanded.add(visibleIndex);
            }
            return newExpanded;
        });
    }

    function updateAutoConstraintSessions(teamId: number, sessions: number): void {
        if (!teamId) return;
        
        autoConstraintSessions.update((map: Record<number, number>) => ({...map, [teamId]: sessions}));
        
        // Find and update the auto constraint for this team
        form.update((f: GenerateScheduleRequest) => {
            const constraints = f.constraints || [];
            const autoConstraintIndex = constraints.findIndex((c: Constraint) => 
                c.team_id === teamId && c.constraint_type === 'auto'
            );
            
            if (autoConstraintIndex !== -1) {
                constraints[autoConstraintIndex] = {
                    ...constraints[autoConstraintIndex],
                    sessions
                };
            }
            
            return {
                ...f,
                constraints
            };
        });
    }

    function removeAutoConstraint(teamId: number): void {
        if (!teamId) return;

        // Remove from the form
        form.update((f: GenerateScheduleRequest) => {
            const constraints = f.constraints || [];
            const newConstraints = constraints.filter((c: Constraint) => 
                !(c.team_id === teamId && c.constraint_type === 'auto')
            );
            
            // Check if this was the last constraint for this team
            const hasRemainingConstraints = newConstraints.some(
                c => c.team_id === teamId
            );

            // If no remaining constraints, remove team from team_ids
            if (!hasRemainingConstraints) {
                return {
                    ...f,
                    constraints: newConstraints,
                    team_ids: (f.team_ids || []).filter(id => id !== teamId)
                };
            }

            return {
                ...f,
                constraints: newConstraints
            };
        });

        // Remove from tracking stores
        autoModeAppliedTeams.update((teams: Set<number>) => {
            teams.delete(teamId);
            return teams;
        });
        
        autoConstraintSessions.update((map: Record<number, number>) => {
            const newMap = {...map};
            delete newMap[teamId];
            return newMap;
        });
    }

    async function autoGenerateConstraint(): Promise<void> {
        if (!selectedTeam?.team_id) return;
        const teamId = selectedTeam.team_id;
        const sessions = selectedTeam.weekly_trainings;
        
        const newConstraint: Constraint = {
            team_id: teamId,
            required_field: null,
            required_cost: selectedTeam.preferred_field_size || selectedTeam.minimum_field_size || null,
            sessions: sessions,
            length: 4,
            day_of_week: null,
            partial_field: null,
            partial_cost: null,
            partial_time: null,
            start_time: null,
            constraint_type: 'auto'
        };

        // Add the constraint
        form.update((f: GenerateScheduleRequest) => ({
            ...f,
            constraints: [...(f.constraints || []), newConstraint]
        }));

        // Ensure the team is selected in the sidebar
        form.update((f: GenerateScheduleRequest) => ({
            ...f,
            team_ids: Array.from(new Set([...(f.team_ids || []), teamId]))
        }));

        autoModeAppliedTeams.update((teams: Set<number>) => {
            teams.add(teamId);
            return teams;
        });
        
        // Initialize the sessions for this team
        autoConstraintSessions.update((map: Record<number, number>) => ({...map, [teamId]: sessions}));
    }
</script>

<div class="detail-card">
    {#if selectedTeam}
        {@const teamId = selectedTeam.team_id}  <!-- Create a constant to help TypeScript infer type -->
        <div class="mb-4">
            <div class="flex flex-col gap-3">
                <div class="flex justify-between items-center">
                    <h3 class="text-lg font-semibold">Constraints for {selectedTeam.name}</h3>
                </div>
                <div class="mb-6">
                    {#if teamId !== undefined && $autoModeAppliedTeams.has(teamId)}
                        <div class="flex items-center gap-3">
                            <div class="flex items-center">
                                <button 
                                    class="px-2 py-1 border border-mint-200 rounded-l hover:bg-mint-50 text-mint-700"
                                    onclick={() => {
                                        const currentSessions = $autoConstraintSessions[teamId] || 1;
                                        if (currentSessions > 1) {
                                            updateAutoConstraintSessions(teamId, currentSessions - 1);
                                        }
                                    }}
                                >
                                    −
                                </button>
                                <div class="px-3 py-1 border-t border-b border-mint-200 min-w-[2.5rem] text-center text-mint-700">
                                    {$autoConstraintSessions[teamId] || 1}
                                </div>
                                <button 
                                    class="px-2 py-1 border border-mint-200 rounded-r hover:bg-mint-50 text-mint-700"
                                    onclick={() => {
                                        const currentSessions = $autoConstraintSessions[teamId] || 1;
                                        if (currentSessions < 7) {
                                            updateAutoConstraintSessions(teamId, currentSessions + 1);
                                        }
                                    }}
                                >
                                    +
                                </button>
                            </div>
                            <div class="flex items-center px-3 py-1.5 bg-mint-100 text-mint-700 rounded-full w-fit">
                                <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                                </svg>
                                Auto mode applied
                            </div>
                            <button 
                                class="p-2 text-red-500 hover:text-red-600 transition-colors duration-200"
                                onclick={() => removeAutoConstraint(teamId)}
                                aria-label="Remove auto constraint"
                            >
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                            </button>
                        </div>
                    {/if}
                    {#if teamId !== undefined && !$autoModeAppliedTeams.has(teamId)}
                        <button 
                            class="btn-secondary text-sm"
                            onclick={() => autoGenerateConstraint()}
                        >
                            Auto generate
                        </button>
                    {/if}
                </div>
            </div>
            {#if $form.constraints}
                {#each $form.constraints.filter((c: Constraint) => c.team_id === selectedTeam.team_id && c.constraint_type !== 'auto') as constraint, visibleIndex}
                    <div class="flex items-center gap-2 mb-4">
                        <div class="constraint-card">
                            <div class="flex flex-row gap-14 flex-wrap items-end">
                                {#if constraint.constraint_type === 'specific'}
                                    {@const actualIndex = getActualIndex(visibleIndex)}
                                    <EditableField
                                        {form}
                                        errors={$errors}
                                        name="constraints[{actualIndex}].sessions"
                                        label="Sessions for this constraint"
                                        type="select"
                                        options={[
                                            { value: 1, label: '1' },
                                            { value: 2, label: '2' },
                                            { value: 3, label: '3' },
                                            { value: 4, label: '4' },
                                            { value: 5, label: '5' },
                                            { value: 6, label: '6' },
                                            { value: 7, label: '7' }
                                        ]}
                                        required
                                    />
                                    <EditableField
                                        {form}
                                        errors={$errors}
                                        name="constraints[{actualIndex}].required_field"
                                        label="Required Field"
                                        type="select"
                                        options={$fields.flatMap(field => [
                                            { value: field.field_id, label: `${field.name} (${field.field_type})` },
                                            ...field.half_subfields.map(half => ({ 
                                                value: half.field_id, 
                                                label: `${half.name} (half of ${field.name})` 
                                            })),
                                            ...field.quarter_subfields.map(quarter => ({ 
                                                value: quarter.field_id, 
                                                label: `${quarter.name} (quarter of ${field.name})` 
                                            }))
                                        ])}
                                    />
                                
                                    <EditableField
                                        {form}
                                        errors={$errors}
                                        name="constraints[{actualIndex}].length"
                                        label="Length"
                                        type="select"
                                        options={[
                                            { value: 1, label: '15 minutes' },
                                            { value: 2, label: '30 minutes' },
                                            { value: 3, label: '45 minutes' },
                                            { value: 4, label: '60 minutes (1 hour)' },
                                            { value: 5, label: '75 minutes' },
                                            { value: 6, label: '90 minutes (1,5 hours)' },
                                            { value: 7, label: '105 minutes' },
                                            { value: 8, label: '120 minutes (2 hours' },
                                            { value: 9, label: '135 minutes' },
                                            { value: 10, label: '150 minutes (2,5 hours)' }
                                        ]}
                                        required
                                    />

                                    <EditableField
                                        {form}
                                        errors={$errors}
                                        name="constraints[{actualIndex}].start_time"
                                        label="Start Time"
                                        type="text"
                                        placeholder="HH:MM:SS"
                                        hide_label_in_view={false}
                                    />

                                    <EditableField
                                        {form}
                                        errors={$errors}
                                        name="constraints[{actualIndex}].day_of_week"
                                        label="Day of Week"
                                        type="select"
                                        options={[
                                            { value: 0, label: 'Monday' },
                                            { value: 1, label: 'Tuesday' },
                                            { value: 2, label: 'Wednesday' },
                                            { value: 3, label: 'Thursday' },
                                            { value: 4, label: 'Friday' },
                                            { value: 5, label: 'Saturday' },
                                            { value: 6, label: 'Sunday' }
                                        ]}
                                    />

                                    <div class="flex justify-end">
                                        <button
                                            class="flex items-center text-mint-600 hover:text-mint-700 mt-2"
                                            onclick={() => togglePartialFields(visibleIndex)}
                                        >
                                            <span class="mr-1">{$expandedConstraints.has(visibleIndex) ? '−' : '+'}</span>
                                            Partial Session Options
                                        </button>
                                    </div>
                                    
                                    {#if $expandedConstraints.has(visibleIndex)}
                                            <EditableField
                                            {form}
                                            errors={$errors}
                                            name="constraints[{actualIndex}].partial_field"
                                            label="Partial Field"
                                            type="select"
                                            options={$fields.flatMap(field => [
                                                { value: field.field_id, label: `${field.name} (${field.field_type})` },
                                                ...field.half_subfields.map(half => ({ 
                                                    value: half.field_id, 
                                                    label: `${half.name} (half of ${field.name})` 
                                                })),
                                                ...field.quarter_subfields.map(quarter => ({ 
                                                    value: quarter.field_id, 
                                                    label: `${quarter.name} (quarter of ${field.name})` 
                                                }))
                                            ])}
                                        />
                                        <EditableField
                                            {form}
                                            errors={$errors}
                                            name="constraints[{actualIndex}].partial_time"
                                            label="Partial Time"
                                            type="select"
                                            options={[
                                                { value: 1, label: '15 minutes' },
                                                { value: 2, label: '30 minutes' },
                                                { value: 3, label: '45 minutes' },
                                                { value: 4, label: '60 minutes (1 hour)' },
                                                { value: 5, label: '75 minutes' },
                                                { value: 6, label: '90 minutes (1,5 hours)' }]}
                                        />
                                    {/if}
                                {:else if constraint.constraint_type === 'flexible'}
                                    {@const actualIndex = getActualIndex(visibleIndex)}
                                    <EditableField
                                        {form}
                                        errors={$errors}
                                        name="constraints[{actualIndex}].sessions"
                                        label="Sessions for this constraint"
                                        type="select"
                                        options={[
                                            { value: 1, label: '1' },
                                            { value: 2, label: '2' },
                                            { value: 3, label: '3' },
                                            { value: 4, label: '4' },
                                            { value: 5, label: '5' },
                                            { value: 6, label: '6' },
                                            { value: 7, label: '7' }
                                        ]}
                                        required
                                    />
                                    <EditableField
                                        {form}
                                        errors={$errors}
                                        name="constraints[{actualIndex}].start_time"
                                        label="Start Time"
                                        type="text"
                                        placeholder="HH:MM:SS"
                                    />

                                    <EditableField
                                        {form}
                                        errors={$errors}
                                        name="constraints[{actualIndex}].day_of_week"
                                        label="Day of Week"
                                        type="select"
                                        options={[
                                            { value: 0, label: 'Monday' },
                                            { value: 1, label: 'Tuesday' },
                                            { value: 2, label: 'Wednesday' },
                                            { value: 3, label: 'Thursday' },
                                            { value: 4, label: 'Friday' },
                                            { value: 5, label: 'Saturday' },
                                            { value: 6, label: 'Sunday' }
                                        ]}
                                    />

                                    <EditableField
                                        {form}
                                        errors={$errors}
                                        name="constraints[{actualIndex}].length"
                                        label="Length"
                                        type="select"
                                        options={[
                                            { value: 1, label: '15 minutes' },
                                            { value: 2, label: '30 minutes' },
                                            { value: 3, label: '45 minutes' },
                                            { value: 4, label: '60 minutes (1 hour)' },
                                            { value: 5, label: '75 minutes' },
                                            { value: 6, label: '90 minutes (1,5 hours)' },
                                            { value: 7, label: '105 minutes' },
                                            { value: 8, label: '120 minutes (2 hours' },
                                            { value: 9, label: '135 minutes' },
                                            { value: 10, label: '150 minutes (2,5 hours)' }
                                        ]}
                                        required
                                    />
                                    <EditableField
                                        {form}
                                        errors={$errors}
                                        name="constraints[{actualIndex}].required_cost"
                                        label="Required Size"
                                        type="select"
                                        options={[
                                            { value: 1000, label: '11v11' },
                                            { value: 500, label: '8v8, Half 11v11' },
                                            { value: 250, label: '5v5, Half 8v8, Quarter 11v11' },
                                            { value: 125, label: '3v3, Half 5v5, Quarter 8v8' }
                                        ]}
                                        view_mode_style="pill"
                                        required
                                    />
                                    <div class="flex justify-end">
                                        <button
                                            class="flex items-center text-mint-600 hover:text-mint-700 mt-2"
                                            onclick={() => togglePartialFields(visibleIndex)}
                                        >
                                            <span class="mr-1">{$expandedConstraints.has(visibleIndex) ? '−' : '+'}</span>
                                            Partial Session Options
                                        </button>
                                    </div>
                                    
                                    {#if $expandedConstraints.has(visibleIndex)}
                                        <EditableField
                                            {form}
                                            errors={$errors}
                                            name="constraints[{actualIndex}].partial_cost"
                                            label="Partial Size"
                                            type="select"
                                            options={[
                                                { value: 1000, label: '11v11' },
                                                { value: 500, label: '8v8, Half 11v11' },
                                                { value: 250, label: '5v5, Half 8v8, Quarter 11v11' }
                                            ]}
                                            view_mode_style="pill"
                                        />
                                        <EditableField
                                            {form}
                                            errors={$errors}
                                            name="constraints[{actualIndex}].partial_time"
                                            label="Partial Time"
                                            type="select"
                                            options={[
                                                { value: 1, label: '15 minutes' },
                                                { value: 2, label: '30 minutes' },
                                                { value: 3, label: '45 minutes' },
                                                { value: 4, label: '60 minutes (1 hour)' },
                                                { value: 5, label: '75 minutes' },
                                                { value: 6, label: '90 minutes (1,5 hours)' }
                                            ]}
                                        />
                                    {/if}
                                {/if}
                            </div>
                        </div>
                        <div class="flex items-center">
                            <button 
                                class="p-2 text-red-500 hover:text-red-600 transition-colors duration-200"
                                onclick={() => removeConstraint(visibleIndex)}
                                aria-label="Remove constraint"
                            >
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                            </button>
                        </div>
                    </div>
                {/each}
            {/if}
            
            {#if !$form.constraints?.filter((c: Constraint) => c.team_id === selectedTeam.team_id && c.constraint_type !== 'auto').length 
                || $form.constraints?.filter((c: Constraint) => c.team_id === selectedTeam.team_id && c.constraint_type !== 'auto').length < 7}
                <div class="relative inline-block mt-6">
                    <button 
                        class="btn-add"
                        onclick={() => {
                            const dropdown = document.getElementById('constraintTypeDropdown');
                            if (dropdown) {
                                dropdown.classList.toggle('hidden');
                            }
                        }}
                    >
                        Add Constraint
                    </button>
                    <div 
                        id="constraintTypeDropdown"
                        class="hidden absolute left-0 top-full mt-2 w-48 bg-white rounded-xl shadow-xl border border-mint-100 z-10"
                    >
                        <div class="dropdown-content">
                            <button
                                class="dropdown-item"
                                onclick={() => {
                                    addConstraint('specific');
                                    document.getElementById('constraintTypeDropdown')?.classList.add('hidden');
                                }}
                            >
                                Specific
                            </button>
                            <button
                                class="dropdown-item"
                                onclick={() => {
                                    addConstraint('flexible');
                                    document.getElementById('constraintTypeDropdown')?.classList.add('hidden');
                                }}
                            >
                                Flexible
                            </button>
                        </div>
                    </div>
                </div>
            {/if}
        </div>
    {:else}
        <p class="text-gray-500">Select a team to add constraints</p>
    {/if}
</div>